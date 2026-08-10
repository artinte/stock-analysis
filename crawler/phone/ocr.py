import easyocr
import pathlib
from PIL import Image, ImageEnhance
import numpy
import cv2

# 保持 reader 全局或在函数外初始化以避免重复加载模型
reader = easyocr.Reader(["ch_sim", "en"])


def _calculate_iou(box1, box2):
    """
    计算两个边界框的 IoU (Intersection over Union)
    边界框格式为：[[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    """
    x1_min = min(p[0] for p in box1)
    y1_min = min(p[1] for p in box1)
    x1_max = max(p[0] for p in box1)
    y1_max = max(p[1] for p in box1)

    x2_min = min(p[0] for p in box2)
    y2_min = min(p[1] for p in box2)
    x2_max = max(p[0] for p in box2)
    y2_max = max(p[1] for p in box2)

    inter_x1 = max(x1_min, x2_min)
    inter_y1 = max(y1_min, y2_min)
    inter_x2 = min(x1_max, x2_max)
    inter_y2 = min(y1_max, y2_max)

    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h
    area1 = (x1_max - x1_min) * (y1_max - y1_min)
    area2 = (x2_max - x2_min) * (y2_max - y2_min)
    union_area = area1 + area2 - inter_area
    if union_area == 0:
        return 0.0
    return inter_area / union_area


def _run_ocr_pipeline(gray_img, scale, threshold, invert):
    processed_img = gray_img.copy()

    if invert:
        img_array = numpy.array(processed_img)
        inverted_array = 255 - img_array
        processed_img = Image.fromarray(inverted_array)

    original_width, original_height = processed_img.size
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    try:
        resample_method = Image.Resampling.LANCZOS
    except AttributeError:
        resample_method = Image.LANCZOS

    resized_img = processed_img.resize((new_width, new_height), resample_method)

    enhancer = ImageEnhance.Contrast(resized_img)
    enhanced_img = enhancer.enhance(2.0)
    img_array = numpy.array(enhanced_img)

    result = reader.readtext(img_array)

    filtered_results = []
    inverse_scale = 1 / scale
    for bbox, text, prob in result:
        text = str(text).strip()
        if prob >= threshold and text:
            restored_bbox = [
                [round(p[0] * inverse_scale), round(p[1] * inverse_scale)] for p in bbox
            ]
            filtered_results.append((restored_bbox, text, prob))
    return filtered_results


def recognize_text(
    uuid,
    scale=0.6,
    threshold=0.05,
    local_dir=None,
    iou_threshold=0.5,  # 调整默认阈值到 0.5，更合理
):
    """
    识别图片中的文字，并通过 IoU 去除同位置重复文字。
    不同位置的相同文本会保留。
    """

    filename = f"{uuid}_screen.png"
    if local_dir:
        file_path = pathlib.Path(local_dir) / filename
    else:
        file_path = pathlib.Path.home() / "Pictures" / filename

    if not file_path.is_file():
        print(f"{uuid} 错误：未找到文件 {file_path}，请确认已先进行截图")
        return []

    final_results = []
    with Image.open(file_path) as img:
        gray_img = img.convert("L")

        results_normal = _run_ocr_pipeline(gray_img, scale, threshold, invert=False)
        results_inverted = _run_ocr_pipeline(gray_img, scale, threshold, invert=True)
        all_results = results_normal + results_inverted

        # 按概率从高到低排序
        all_results.sort(key=lambda x: x[2], reverse=True)

        keep_flags = [True] * len(all_results)

        for i, (box_i, text_i, prob_i) in enumerate(all_results):
            if not keep_flags[i] or not text_i:
                continue

            # 保留该结果
            final_results.append((box_i, text_i, prob_i))

            for j in range(i + 1, len(all_results)):
                if not keep_flags[j]:
                    continue
                box_j, text_j, prob_j = all_results[j]

                # 仅当文本完全一致时才检查位置重叠
                if text_i == text_j:
                    iou = _calculate_iou(box_i, box_j)
                    # 如果位置重叠度高，则判为重复
                    if iou >= iou_threshold:
                        keep_flags[j] = False

    return final_results


# 示例：
# print(recognize_text("905ee636"))
# print(recognize_text("9598552235004UD"))
# print(recognize_text("e62ee489"))


def is_contour_closed(contour):
    """
    判断轮廓是否闭合：轮廓的第一个点和最后一个点是否接近（误差在2像素内）
    """
    if len(contour) < 4:  # 至少4个点才可能形成闭合轮廓
        return False
    # 轮廓的第一个点和最后一个点（OpenCV轮廓格式为[[x,y]]）
    first = contour[0][0]
    last = contour[-1][0]
    # 计算两点距离（小于2像素视为闭合）
    distance = numpy.linalg.norm(first - last)
    return distance < 2


def get_closed_contours(uuid, local_dir=None):
    """
    提取所有闭合轮廓，返回外围坐标列表[(x1,y1,x2,y2), ...]
    """
    filename = f"{uuid}_screen.png"
    # 构建文件路径
    if local_dir:
        file_path = pathlib.Path(local_dir) / filename
    else:
        file_path = pathlib.Path.home() / "Pictures" / filename

    # 检查文件是否存在
    if not file_path.is_file():
        print(f"{uuid} 错误：未找到文件 {file_path}，请确认已先进行截图")
        return []

    # 读取图像并转换为OpenCV格式
    try:
        with Image.open(file_path) as pil_img:
            # PIL图像转OpenCV（RGB -> BGR）
            image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"{uuid} 错误：读取图像失败 - {e}")
        return []

    # 获取图像尺寸
    h, w = image.shape[:2]  # 修正：之前误写为image未定义

    # 1. 预处理：增强边缘
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)  # 提取边缘

    # 2. 查找所有轮廓（包括内部轮廓）
    contours, _ = cv2.findContours(
        edges.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE
    )

    closed_contours = []
    for contour in contours:
        # 3. 过滤非闭合轮廓
        if not is_contour_closed(contour):
            continue

        # 4. 过滤面积过小的轮廓（排除噪点）
        area = cv2.contourArea(contour)
        if area < 200:  # 最小面积阈值（可根据实际场景调整）
            continue

        # 5. 获取轮廓的最小外接矩形（外围坐标）
        x, y, cw, ch = cv2.boundingRect(contour)
        x1, y1 = x, y
        x2, y2 = x + cw, y + ch

        closed_contours.append((x1, y1, x2, y2))

    # 6. 去重：移除完全重叠的轮廓
    unique_contours = []
    for c in closed_contours:
        if c not in unique_contours:
            unique_contours.append(c)

    return unique_contours
