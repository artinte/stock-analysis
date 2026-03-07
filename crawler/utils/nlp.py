def score_text(text, keywords):
    """根据关键词权重计算‘国家意志’强度"""
    score = 0
    for word in keywords:
        score += text.count(word)
    return score
