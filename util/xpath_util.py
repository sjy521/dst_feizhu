from lxml import html


def find_element_coordinates(xml_path, text):
    """
    从 XML 中根据文本查找元素的坐标
    :param xml_path: xml 地址
    :param text: 元素文本名称
    :return:
    """
    tree = html.etree.parse(xml_path)
    elements = tree.xpath("//node[@text='{}']/@bounds".format(text))
    if elements:
        # 假设只找到一个元素，获取其坐标
        bounds = elements[0]
        if bounds == "[0,0][0,0]":
            elements = tree.xpath("//node[@text='{}']/preceding-sibling::*[1]/@bounds".format(text))
            if elements:
                # 假设只找到一个元素，获取其坐标
                bounds = elements[0]
            else:
                return None
        print(bounds)
        left, top, right, bottom = eval(bounds.replace('][', ","))
        x = (left + right) // 2
        y = (top + bottom) // 2
        return [x, y]
    else:
        return None


def find_element(xml_path, xpath):
    """
    根据xpath 查找
    :param xml_path:
    :param text:
    :return:
    """
    tree = html.etree.parse(xml_path)
    elements = tree.xpath(xpath)
    return elements if elements else None

