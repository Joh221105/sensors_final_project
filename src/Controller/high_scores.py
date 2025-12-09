import time

# game mode lists - campaign = regular
MODES = ["CAMPAIGN", "ENDLESS"]

def load_high_scores(mode="CAMPAIGN"):
    """loads high scores for a specific mode"""
    print(f"[HIGH_SCORES] Loading {mode} scores...")
    
    filename = f"/scores_{mode.lower()}.txt"
    
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
            scores = []
            for line in lines:
                line = line.strip()
                if line:
                    parts = line.split(",")
                    if len(parts) == 3:
                        initials = parts[0]
                        score = int(parts[1])
                        difficulty = parts[2]
                        scores.append({"initials": initials, "score": score, "difficulty": difficulty})
            print(f"[HIGH_SCORES] Loaded {len(scores)} {mode} scores")
            return scores
    except OSError as e:
        print(f"[HIGH_SCORES] File not found for {mode}: {e}")
        return []
    except Exception as e:
        print(f"[HIGH_SCORES] Error loading {mode}: {e}")
        return []

def save_high_scores(scores, mode="CAMPAIGN"):
    """saves high scores for a specific mode"""
    print(f"[HIGH_SCORES] Attempting to save {len(scores)} {mode} scores...")
    
    filename = f"/scores_{mode.lower()}.txt"
    
    try:
        content = ""
        for entry in scores:
            line = f"{entry['initials']},{entry['score']},{entry['difficulty']}\n"
            content += line
            print(f"[HIGH_SCORES] Preparing: {line.strip()}")
        
        print(f"[HIGH_SCORES] Opening {filename} for writing...")
        with open(filename, "w") as f:
            f.write(content)
        
        print(f"[HIGH_SCORES] {mode} save successful!")
        return True
        
    except OSError as e:
        print(f"[HIGH_SCORES] x OSError: {e}")
        return False
    except Exception as e:
        print(f"[HIGH_SCORES] x Error saving {mode}: {e}")
        return False

def is_high_score(score, mode="CAMPAIGN"):
    """Check if score makes the top 3 for a specific mode"""
    print(f"[HIGH_SCORES] Checking if {score} is a {mode} high score...")
    scores = load_high_scores(mode)
    
    # if less than 3 high scores, automatically add as high score
    if len(scores) < 3:
        print(f"[HIGH_SCORES]{len(scores)} {mode} scores recorded!")
        return True
    
    # check if score beats the lowest top 3 score
    lowest_top_score = min(s["score"] for s in scores)
    is_high = score > lowest_top_score
    print(f"[HIGH_SCORES] {'Yes' if is_high else 'No'} (lowest top 3: {lowest_top_score})")
    return is_high

def add_high_score(initials, score, difficulty, mode="CAMPAIGN"):
    """add a new high score and record top 3 for each mode"""
    print(f"[HIGH_SCORES] Adding {mode}: {initials} - {score} ({difficulty})")
    
    scores = load_high_scores(mode)
    
    # add new score
    scores.append({"initials": initials, "score": score, "difficulty": difficulty})
    
    # sort by score (high -> low)
    scores.sort(key=lambda x: x["score"], reverse=True)
    
    # keep only top 3 scores
    scores = scores[:3]
    
    # save to file
    success = save_high_scores(scores, mode)
    
    if success:
        print(f"[HIGH_SCORES] {mode} high score added successfully!")
    else:
        print(f"[HIGH_SCORES] Failed to save {mode} (see errors above)")
    
    return scores

def get_rank(score, mode="CAMPAIGN"):
    """Get what rank this score would be (1-3, or None if not top 3)"""
    scores = load_high_scores(mode)
    scores.append({"initials": "XX", "score": score, "difficulty": "TEST"})
    scores.sort(key=lambda x: x["score"], reverse=True)
    
    for i, entry in enumerate(scores):
        if entry["score"] == score and entry["initials"] == "XX":
            rank = i + 1
            return rank if rank <= 3 else None
    return None
