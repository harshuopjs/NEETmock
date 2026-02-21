def predict_rank(score, total_marks):
    """
    Predicts NEET All India Rank based on score.
    Based on rough historical trends (simplified).
    """
    percentage = (score / total_marks) * 100
    
    # Approximate Rank mapping (Score -> Rank)
    # 720-700 -> Top 50
    # 700-650 -> 50 - 1,000
    # 650-600 -> 1,000 - 10,000
    # 600-500 -> 10,000 - 50,000
    # 500-400 -> 50,000 - 1,50,000
    # 400-300 -> 1,50,000 - 3,00,000
    # < 300 -> > 3,00,000
    
    # We adjust logic based on percentage since total marks might vary (180 vs 60 questions)
    # NEET usually is 720 marks.
    
    # Normalize score to 720 scale for estimation
    normalized_score = (score / total_marks) * 720
    
    rank_range = "Unranked"
    performance_band = "Needs Improvement"
    
    if normalized_score >= 700:
        rank_range = "1 - 50"
        performance_band = "Top 0.01%"
    elif normalized_score >= 650:
        rank_range = "50 - 1,000"
        performance_band = "Top 1%"
    elif normalized_score >= 600:
        rank_range = "1,000 - 10,000"
        performance_band = "Top 5%"
    elif normalized_score >= 500:
        rank_range = "10,000 - 50,000"
        performance_band = "Top 10%"
    elif normalized_score >= 400:
        rank_range = "50,000 - 1,50,000"
        performance_band = "Average"
    elif normalized_score >= 300:
        rank_range = "1,50,000 - 3,00,000"
        performance_band = "Below Average"
    else:
        rank_range = "> 3,00,000"
        performance_band = "Needs Hard Work"

    return {
        "rank_range": rank_range,
        "performance_band": performance_band,
        "normalized_score": round(normalized_score, 2)
    }
