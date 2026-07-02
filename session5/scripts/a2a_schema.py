
class A2AMessage:
    def __init__(self, task, steps, ingredients=None):
        self.task = task
        self.steps = steps
        self.ingredients = ingredients or []

    def to_dict(self):
        return {
            "task": self.task,
            "steps": self.steps,
            "ingredients": self.ingredients
        }

    @staticmethod
    def from_dict(data):
        return A2AMessage(
            task=data.get("task"),
            steps=data.get("steps", []),
            ingredients=data.get("ingredients", [])
        )