from PIL import Image
import pytesseract
import cv2


def get_target_coordinates(target_text, image_path):
    """
    查找目标文字在图片中的位置
    :param target_text:
    :return:
    """
    image = cv2.imread(image_path)
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 定义红色的 HSV 范围
    lower_red = (0, 100, 100)
    upper_red = (10, 255, 255)

    # 创建红色掩码
    red_mask = cv2.inRange(hsv_image, lower_red, upper_red)

    # 使用掩码过滤图像
    filtered_image = cv2.bitwise_and(image, image, mask=red_mask)


    # 使用 Tesseract OCR 识别文本
    text_data = pytesseract.image_to_data(Image.fromarray(filtered_image), lang='chi_sim', output_type='dict')

    # text_data = pytesseract.image_to_data(Image.open(image_path), lang='chi_sim', output_type='dict')

    # 初始化结果列表
    target_positions = []
    print(text_data['text'])
    # 遍历每个识别的文本块
    for i, text in enumerate(text_data['text']):
        if text == target_text:
            # 获取目标文字的坐标信息
            left = text_data['left'][i]
            top = text_data['top'][i]
            width = text_data['width'][i]
            height = text_data['height'][i]

            # 计算目标文字的中心坐标
            center_x = left + width / 2
            center_y = top + height / 2

            # 将坐标信息添加到结果列表
            target_positions.append((center_x, center_y))
    return target_positions


if __name__ == '__main__':
    print(get_target_coordinates('待付款', "./image.PNG"))
