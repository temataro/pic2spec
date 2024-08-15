#!/usr/bin/env python3

import scipy
import numpy as np
import numpy.typing as npt
import matplotlib.image
import matplotlib.pyplot as plt


# TODO: CLI args
# filename: str = "./images/trollface.png"
filename: str = "./images/Lena.png"


def read_img(filename: str) -> npt.NDArray[np.uint8]:
    img: npt.NDArray[np.uint8] = matplotlib.image.imread(filename)

    if img.shape[2] == 3:
        # Convert to greyscale with these magic numbers
        img = img.dot([0.07, 0.72, 0.21])
        return img

    if img.shape[2] == 4:
        # Convert to greyscale with these magic numbers
        img = img.dot([0.07, 0.72, 0.21, 0])
        return img

    plt.imshow(img, cmap='grey')
    plt.show()

    return img


def upscale(row: npt.NDArray[np.uint8]) -> npt.NDArray[np.float32]:
    "Upscale non power of 2 rows to the nearest power of 2."

    width: int = row.size
    if width == 2 ** np.floor(np.log2(width)):
        return np.roll(row, width // 2)

    next_pow: int = int(2 ** (np.ceil(np.log2(width))))
    till_next_pow: int = next_pow - width

    # Rolling makes sure our image's not going to start at 0, but rather at
    # -next_pow // 2  

    # pad before and after to fill the space
    return np.roll(np.pad(
        row, (till_next_pow // 2, till_next_pow // 2 + till_next_pow % 2)
    ).astype(np.float32), next_pow // 2)


def img_to_intensity(img: npt.NDArray[np.uint8]) -> npt.NDArray[np.float32]:
    width: int = img.shape[0]
    height: int = img.shape[1]

    intensity: npt.NDArray[np.float32] = np.array(
        [np.fft.ifft(upscale(np.hstack((img[row][::-1], img[row][:-2])))) for row in range(width - 1, 0, -1)]
    ).flatten()

    plt.specgram(intensity, cmap='grey')
    plt.show()

    return (intensity.real - np.mean(intensity.real)).astype(np.float32)


def intensity_to_wav(audio: npt.NDArray[np.float32], samp_rate: int) -> None:
    outfile: str = f"./audio/{filename.replace("/", "").split(".")[-2]}.wav"
        
    scipy.io.wavfile.write(outfile, samp_rate, audio)


def main() -> None:
    img: npt.NDArray[np.uint8] = read_img(filename)
    audio: npt.NDArray[np.float32] = img_to_intensity(img)
    sr: int = int(44.1e3)

    intensity_to_wav(audio, sr)


if __name__ == "__main__":
    main()
