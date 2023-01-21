# Best Practice
# It's best practice to pass a dict in and out of each function.
# Each function can modify the dict as they complete their computation.
# This design seems the most readable and extensible.
import sequential_functions as sf

def main():
    sequence = sf.Compose(
        create_task_dict,
        load_image,
        preprocess_image,
        detect_objects,
    )

    paths = ["cat.jpg","dog.jpg"]
    for task in sequence(paths):
        print(f"Results: {task['image_path']}")
        print(task["detections"])
        print()

def create_task_dict(path):
    print(f"Tasking: {path}")
    task = { "image_path": path}
    return task

def load_image(task):
    print(f"Loading: {task['image_path']}")
    task["image"] = "e.g. numpy array"
    return task

def preprocess_image(task):
    print(f"Preprocessing: {task['image_path']}")
    task["tensor"] = "e.g. torch tensor"
    return task

def detect_objects(task):
    print(f"Detecting: {task['image_path']}")
    task["detections"] = ["box 1", "box 2"]
    return task

if __name__ == "__main__":
    main()