import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from torch.utils.data import DataLoader, Dataset
from sklearn.preprocessing import RobustScaler
from datetime import datetime, timedelta
from dotenv import dotenv_values
from gateways.data_manager import DataManager
from models.constants import Interval


# --- 1. 模型定义：增加梯度稳定性设计 ---
class EnhancedTransformer(nn.Module):
    def __init__(self, feature_dim=8, model_dim=256, nhead=8, num_layers=3, pred_len=5):
        super().__init__()
        self.input_fc = nn.Linear(feature_dim, model_dim)
        # 加入可学习的位置编码
        self.pos_emb = nn.Parameter(torch.zeros(1, 100, model_dim))

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=model_dim,
            nhead=nhead,
            dim_feedforward=256,
            dropout=0.1,
            batch_first=True,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.output_fc = nn.Linear(model_dim, pred_len)

    def forward(self, x):
        # x shape: [batch, seq_len, feature_dim]
        x = self.input_fc(x) + self.pos_emb[:, : x.size(1), :]
        x = self.transformer(x)
        return self.output_fc(x[:, -1, :])


# --- 2. 数据集：严格处理无效值 ---
class StockDataset(Dataset):
    def __init__(self, data, seq_len=60, pred_len=5):
        self.data = data
        self.seq_len = seq_len
        self.pred_len = pred_len

    def __len__(self):
        return len(self.data) - self.seq_len - self.pred_len

    def __getitem__(self, idx):
        x = self.data[idx : idx + self.seq_len]
        # 目标：未来 5 天相对于当前收盘价的累计变化
        # Close 位于 features 的第 3 列 (index 3: o,h,l,c,v...)
        current_close = self.data[idx + self.seq_len - 1, 3]
        future_closes = self.data[
            idx + self.seq_len : idx + self.seq_len + self.pred_len, 3
        ]

        # 避免除以 0
        y = (future_closes - current_close) / (current_close + 1e-9)
        return torch.FloatTensor(x), torch.FloatTensor(y)


# --- 3. 主程序逻辑 ---
config = dotenv_values("private_config.txt")
dm = DataManager(provider_name="yinhe")
STOCK_CODE = "600519.SH"  # 贵州茅台

if dm.start(config):
    try:
        # 1. 获取 10 年数据
        klines = dm.get_kline(
            STOCK_CODE,
            Interval.DAY_1,
            datetime.now() - timedelta(days=365 * 20),
            datetime.now(),
        )

        # 2. 特征工程 & 查杀 NaN
        df = pd.DataFrame(
            [
                {"o": k.open, "h": k.high, "l": k.low, "c": k.close, "v": k.volume}
                for k in klines
            ]
        )

        # 计算辅助指标
        df["ret"] = df["c"].pct_change()
        df["volat"] = df["ret"].rolling(10).std()
        ma20 = df["c"].rolling(20).mean()
        df["ma_dist"] = (df["c"] - ma20) / (ma20 + 1e-9)

        # 核心：处理所有的 nan 和 inf
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.fillna(method="ffill", inplace=True)  # 向前填充
        df.fillna(0, inplace=True)  # 依然有 nan 则补 0

        features_list = ["o", "h", "l", "c", "v", "ret", "volat", "ma_dist"]
        data_matrix = df[features_list].values

        # 3. 归一化
        scaler = RobustScaler()
        scaled_data = scaler.fit_transform(data_matrix)
        # 剪裁极端异常值，防止梯度爆炸
        scaled_data = np.clip(scaled_data, -5, 5)

        # 4. 训练准备
        SEQ_LEN, PRED_LEN = 60, 5
        dataset = StockDataset(scaled_data, SEQ_LEN, PRED_LEN)
        loader = DataLoader(dataset, batch_size=64, shuffle=True)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = EnhancedTransformer(feature_dim=len(features_list)).to(device)
        optimizer = optim.AdamW(model.parameters(), lr=1e-4)
        criterion = nn.HuberLoss()  # 对离群点比 MSE 更友好

        # 5. 训练循环
        model.train()
        print(f"开始基于 20 年数据训练 (设备: {device})...")
        for epoch in range(1000):
            total_loss = 0
            for bx, by in loader:
                bx, by = bx.to(device), by.to(device)

                optimizer.zero_grad()
                pred = model(bx)
                loss = criterion(pred, by)

                # 检查 loss 是否为 nan
                if torch.isnan(loss):
                    continue

                loss.backward()
                # 核心：梯度裁剪，彻底解决 nan 崩溃问题
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()

                total_loss += loss.item()

            if (epoch + 1) % 200 == 0:
                print(f"Epoch {epoch+1}, Avg Loss: {total_loss/len(loader):.6f}")

        # 6. 推理预测
        model.eval()
        with torch.no_grad():
            last_window = (
                torch.FloatTensor(scaled_data[-SEQ_LEN:]).unsqueeze(0).to(device)
            )
            raw_preds = model(last_window).cpu().numpy().flatten()

            last_close = klines[-1].close
            print(f"\n--- 600519.SH 未来 5 日预测 (当前: {last_close:.2f}) ---")
            for i, r in enumerate(raw_preds):
                target_p = last_close * (1 + r)
                print(f"T+{i+1}: {target_p:.2f} (幅度: {r*100:+.2f}%)")

    finally:
        dm.stop()
