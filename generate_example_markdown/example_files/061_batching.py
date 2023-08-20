# Batching
# Use batching to collate multiple items into a batch.
# A machine learning model may more efficient on batches.
import sequential_functions as sf
import time
def main():
    sequence = sf.Compose(
        # Build the batches in background processes.
        sf.Compose(
            load_image,
            sf.Batch(batch_size=3),
            collate_images,
            num_processes=3, 
        ),
        # Detect in the main process.
        detect_objects,
        debatch_detections,
    )

    image_paths = (f"image_{i}.jpg" for i in range(10))

    results = list(sequence(image_paths))
    for result in results:
        print(result)

def load_image(path):
    return path.replace("image","tensor").replace(".jpg","")

def collate_images(x_list):
    # Ideally you would stack images into a tensor
    return ",".join(x_list)

def detect_objects(x_batch):
    print(f"Detecting on Batch: {x_batch}")
    # Ideally your detection runs faster with a batch of images.
    return x_batch.replace("tensor","Detections tensor")

def debatch_detections(x_batch):
    yield from x_batch.split(",")

if __name__ == "__main__":
    main()