import math
import random

class Node:
    def __init__(self, feature=None, threshold=None, left=None, right=None, value=None):
        self.feature = feature          # index of feature to split on
        self.threshold = threshold      # threshold value for numerical split
        self.left = left                # left child
        self.right = right              # right child
        self.value = value              # prediction value if leaf node

    def is_leaf(self):
        return self.value is not None

class DecisionTree:
    def __init__(self, max_depth=5, min_samples_split=2):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root = None

    def _entropy(self, y):
        if not y:
            return 0.0
        counts = {}
        for val in y:
            counts[val] = counts.get(val, 0) + 1
        entropy = 0.0
        n = len(y)
        for val, count in counts.items():
            p = count / n
            entropy -= p * math.log2(p)
        return entropy

    def _split(self, X, y, idx, threshold):
        left_idx = [i for i, row in enumerate(X) if row[idx] <= threshold]
        right_idx = [i for i, row in enumerate(X) if row[idx] > threshold]
        
        X_left = [X[i] for i in left_idx]
        y_left = [y[i] for i in left_idx]
        X_right = [X[i] for i in right_idx]
        y_right = [y[i] for i in right_idx]
        
        return X_left, y_left, X_right, y_right

    def _best_split(self, X, y):
        best_gain = -1.0
        best_idx = None
        best_threshold = None
        
        n_samples = len(X)
        if n_samples <= 0:
            return None, None
            
        n_features = len(X[0])
        current_entropy = self._entropy(y)
        
        for idx in range(n_features):
            # Extract unique values of this feature to test as split points
            values = sorted(list(set(row[idx] for row in X)))
            
            # Test split thresholds midway between adjacent values
            thresholds = []
            for i in range(len(values) - 1):
                thresholds.append((values[i] + values[i+1]) / 2.0)
            if len(values) == 1:
                thresholds.append(values[0])
                
            for thresh in thresholds:
                _, y_l, _, y_r = self._split(X, y, idx, thresh)
                if not y_l or not y_r:
                    continue
                    
                n_l, n_r = len(y_l), len(y_r)
                gain = current_entropy - ((n_l / n_samples) * self._entropy(y_l) + (n_r / n_samples) * self._entropy(y_r))
                
                if gain > best_gain:
                    best_gain = gain
                    best_idx = idx
                    best_threshold = thresh
                    
        return best_idx, best_threshold

    def _most_common_label(self, y):
        if not y:
            return None
        counts = {}
        for val in y:
            counts[val] = counts.get(val, 0) + 1
        return max(counts, key=counts.get)

    def _build_tree(self, X, y, depth=0):
        n_samples = len(X)
        n_features = len(X[0]) if n_samples > 0 else 0
        
        # Base cases: pure node, max depth, or insufficient samples
        if (depth >= self.max_depth or 
            n_samples < self.min_samples_split or 
            len(set(y)) == 1):
            return Node(value=self._most_common_label(y))
            
        # Find best split
        idx, thresh = self._best_split(X, y)
        if idx is None:
            return Node(value=self._most_common_label(y))
            
        # Perform split
        X_l, y_l, X_r, y_r = self._split(X, y, idx, thresh)
        
        # Build subtrees
        left_child = self._build_tree(X_l, y_l, depth + 1)
        right_child = self._build_tree(X_r, y_r, depth + 1)
        
        return Node(feature=idx, threshold=thresh, left=left_child, right=right_child)

    def fit(self, X, y):
        self.root = self._build_tree(X, y)

    def _predict_row(self, node, x):
        if node.is_leaf():
            return node.value
        if x[node.feature] <= node.threshold:
            return self._predict_row(node.left, x)
        else:
            return self._predict_row(node.right, x)

    def predict(self, X):
        return [self._predict_row(self.root, x) for x in X]

# ----------------- RISK EVALUATOR INTERFACE -----------------

class LeaveRiskPredictor:
    def __init__(self):
        self.staffing_tree = DecisionTree(max_depth=4)
        self.deadline_tree = DecisionTree(max_depth=4)
        self._train_models()

    def _train_models(self):
        # 1. Staffing Risk training data generation
        # Features: [team_size, overlap_count, overlap_ratio, active_tasks]
        # Target: Risk level (0=Low, 1=Medium, 2=High)
        X_staffing = []
        y_staffing = []
        
        # Seed for reproducible behavior
        random.seed(42)
        
        for _ in range(500):
            team_size = random.randint(2, 10)
            overlap_count = random.randint(0, team_size - 1)
            overlap_ratio = overlap_count / team_size
            active_tasks = random.randint(0, 8)
            
            # Business rules
            if overlap_ratio >= 0.45 or (overlap_count >= 2 and team_size <= 4):
                risk = 2 # High
            elif overlap_ratio >= 0.2 or (overlap_count >= 1 and team_size <= 3) or active_tasks >= 5:
                risk = 1 # Medium
            else:
                risk = 0 # Low
                
            X_staffing.append([team_size, overlap_count, overlap_ratio, active_tasks])
            y_staffing.append(risk)
            
        self.staffing_tree.fit(X_staffing, y_staffing)

        # 2. Deadline Risk training data generation
        # Features: [days_to_deadline, busy_season (0/1), employee_tasks]
        # Target: Risk level (0=Safe, 1=Risky, 2=Critical)
        X_deadline = []
        y_deadline = []
        
        for _ in range(500):
            days_to_deadline = random.randint(1, 30)
            busy_season = random.choice([0, 1])
            employee_tasks = random.randint(0, 5)
            
            # Business rules
            if days_to_deadline <= 3 or (days_to_deadline <= 6 and busy_season == 1):
                risk = 2 # Critical
            elif days_to_deadline <= 8 or (busy_season == 1 and days_to_deadline <= 14) or employee_tasks >= 3:
                risk = 1 # Risky
            else:
                risk = 0 # Safe
                
            X_deadline.append([days_to_deadline, busy_season, employee_tasks])
            y_deadline.append(risk)
            
        self.deadline_tree.fit(X_deadline, y_deadline)

    def evaluate_leave(self, team_size, overlap_count, active_tasks, days_to_deadline, busy_season, employee_tasks):
        """
        Evaluate leave request parameters and return predictions.
        """
        overlap_ratio = overlap_count / team_size if team_size > 0 else 0.0
        
        # Predict Staffing Risk
        staffing_feat = [team_size, overlap_count, overlap_ratio, active_tasks]
        staffing_pred = self.staffing_tree.predict([staffing_feat])[0]
        
        # Predict Deadline Risk
        deadline_feat = [days_to_deadline, 1 if busy_season else 0, employee_tasks]
        deadline_pred = self.deadline_tree.predict([deadline_feat])[0]
        
        # Map back to labels
        staffing_labels = {0: "Low", 1: "Medium", 2: "High"}
        deadline_labels = {0: "Safe", 1: "Risky", 2: "Critical"}
        
        staffing_risk = staffing_labels.get(staffing_pred, "Low")
        deadline_risk = deadline_labels.get(deadline_pred, "Safe")
        
        # Safe approval recommendation
        if staffing_risk == "High" or deadline_risk == "Critical":
            recommendation = "Reject (High Risk of operations coverage or deadline collision)"
            is_safe = False
        elif staffing_risk == "Medium" or deadline_risk == "Risky":
            recommendation = "Review Carefully (Moderate staffing or task deadline proximity)"
            is_safe = True
        else:
            recommendation = "Safe to Approve"
            is_safe = True
            
        return {
            "staffing_risk": staffing_risk,
            "deadline_risk": deadline_risk,
            "recommendation": recommendation,
            "is_safe": is_safe,
            "overlap_ratio_pct": round(overlap_ratio * 100, 1)
        }

# Global singleton predictor instance
predictor = LeaveRiskPredictor()
