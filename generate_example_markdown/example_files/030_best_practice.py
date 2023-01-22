# Best Practice
# It's best practice to pass a dict in and out of each function.
# Each function can modify the dict as they complete their computation.
# This design seems the most readable and extensible.
import sequential_functions as sf

def main():
    sequence = sf.Compose(
        create_item_dict,
        load_image,
        preprocess_image,
        detect_objects,
    )

    paths = ["cat.jpg","dog.jpg"]
    for item in sequence(paths):
        print(f"Results: {item['image_path']}")
        print(item["detections"])
        print()

def create_item_dict(path):
    print(f"Item Dict: {path}")
    item = { "image_path": path}
    return item

def load_image(item):
    print(f"Loading: {item['image_path']}")
    item["image"] = "e.g. numpy array"
    return item

def preprocess_image(item):
    print(f"Preprocessing: {item['image_path']}")
    item["tensor"] = "e.g. torch tensor"
    return item

def detect_objects(item):
    print(f"Detecting: {item['image_path']}")
    item["detections"] = ["box 1", "box 2"]
    return item

if __name__ == "__main__":
    main()