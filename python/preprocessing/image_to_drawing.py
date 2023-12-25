import cv2
import copy

# contrast : 0-255, resolution: tuple

def grayscale(img,contrast):
    h = len(img)
    w = len(img[0])
    for y in range(0, h):
        for x in range(0, w):
            # threshold the pixel
            img[y, x] = 255 if img[y, x] >= contrast else 0
    return img
def consolidate_pixels(image,depth,contrast):
    image = grayscale(image,contrast)
    img_copy = copy.deepcopy(image)
    neighbors = 1
    if (neighbors):
        for y in range(depth, h-depth):
            for x in range(depth, w-depth):
                same_val = True
                curr_pixel_val = img_copy[y][x]
                for y1 in range(y-depth, y+depth+1):
                    for x1 in range(x-depth, x+depth+1):
                        neighbor_val = image[y1][x1]
                        same_val = same_val and curr_pixel_val == neighbor_val
                # threshold the pixel
                image[y, x] = curr_pixel_val if same_val else 255
    return image
def drawing_img(file_path, contrast, resolution):
    depth = 1
    img = cv2.imread(file_path)
    img = cv2.resize(img, (1080, 1080),
                     interpolation=cv2.INTER_NEAREST,)
    alpha = 2  # Contrast control (1.0-3.0)
    beta = 0  # Brightness control (0-100)

    adjusted = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

    grey_img = cv2.cvtColor(adjusted, cv2.COLOR_BGR2GRAY)
    invert_img = cv2.bitwise_not(grey_img)
    blur_img = cv2.GaussianBlur(invert_img, (111, 111), 0)
    invblur_img = cv2.bitwise_not(blur_img)
    sketch_img = cv2.divide(grey_img, invblur_img, scale=256.0)
    adjusted = cv2.convertScaleAbs(sketch_img, alpha=alpha, beta=beta)
    image = sketch_img.copy()
    # loop over the image, pixel by pixel
    h = image.shape[0]
    w = image.shape[1]

    small_image = cv2.resize(
        image, resolution, interpolation=cv2.INTER_LINEAR)
    large_image = cv2.resize(small_image, (1080, 1080),
                             interpolation=cv2.INTER_NEAREST,)
    large_image = grayscale(large_image,contrast)

    return img, large_image


if __name__ == "__main__":
    image, large = drawing_img("images/image2.jpg", 220, (140,140))
    large = cv2.resize(
        large, (140,140), interpolation=cv2.INTER_LINEAR)
    #cv2.imshow('original.png', image)
    cv2.imshow('new.png', large)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
