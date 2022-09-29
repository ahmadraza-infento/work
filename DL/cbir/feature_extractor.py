from skimage.io import imread, imshow, imsave
from skimage.feature import hog
from skimage.transform import resize




def get_hog(img_path):
    img = imread(img_path)
    resized_img = resize(img, (64,128)) 
    fd, hog_image = hog(resized_img, orientations=9, pixels_per_cell=(8, 8), 
                        cells_per_block=(2, 2), visualize=True, multichannel=True)

    imsave("test.jpg", arr=img)
    return fd


if __name__ == "__main__":
    img_path = "SigExamples/Example1.jpg"
    get_hog(img_path)