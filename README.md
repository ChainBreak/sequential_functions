# Sequential Functions
Compose functions into a sequence that are called sequentially.

Under the hood, functions are wrapped in generators so that a sequence can be composed as a generator chain.

# Examples
```Python
import sequential_functions as sf

def main():
    sequence = sf.Compose([
        load_image,
        convert_grayscale,
        theshold,
    ])

    path_list = ["cat.jpg", "dog.jpg"]

    # pull the paths through the sequence one by one
    for image in sequence(path_list):
        cv2.imshow(image)
        cv2.waitKey(1000)

def load_image(path):
    return cv2.imread(path)

def convert_grayscale(image)
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def theshold(image):
    return cv2.threshold(img,127,255,cv.THRESH_BINARY)

```
