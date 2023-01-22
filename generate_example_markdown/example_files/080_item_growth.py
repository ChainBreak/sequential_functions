# Item Growth
# Functions can yield out more items than they take in.
import sequential_functions as sf

def main():
    sequence = sf.Compose(
        yield_video_frames,
        detect_objects,
    )
    for x in sequence(range(3)):
        print(x)

def yield_video_frames(x):
    num_frames = 3
    for i in range(num_frames):
        yield f"Video {x}, Frame {i}"

def detect_objects(x):
    return f" Detecting objects in {x}"

if __name__ == "__main__":
    main()