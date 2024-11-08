from lxml import html


def find_element_coordinates(xml_path, text):
    """
    从 XML 中根据文本查找元素的坐标，没有就匹配后一个坐标
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
                print("...")
                return None
        print(bounds)
        left, top, right, bottom = eval(bounds.replace('][', ","))
        x = (left + right) // 2
        y = (top + bottom) // 2
        return [x, y]
    else:
        print("未发现element")
        return None


def find_setting(xml_path, text):
    """
    匹配设置
    :param xml_path: xml 地址
    :param text: 元素文本名称
    :return:
    """
    tree = html.etree.parse(xml_path)
    elements = tree.xpath("//node[@content-desc='{}']/@bounds".format(text))
    if elements:
        # 假设只找到一个元素，获取其坐标
        bounds = elements[0]
        if bounds == "[0,0][0,0]":
            elements = tree.xpath("//node[@content-desc='{}']/preceding-sibling::*[1]/@bounds".format(text))
            if elements:
                # 假设只找到一个元素，获取其坐标
                bounds = elements[0]
            else:
                print("...")
                return None
        print(bounds)
        left, top, right, bottom = eval(bounds.replace('][', ","))
        x = (left + right) // 2
        y = (top + bottom) // 2
        return [x, y]
    else:
        print("未发现element")
        return None


def find_current_element_coordinates(xml_path, text):
    """
    从 XML 中根据文本查找元素的坐标，不会匹配后一个坐标
    :param xml_path: xml 地址
    :param text: 元素文本名称
    :return:
    """
    tree = html.etree.parse(xml_path)
    elements = tree.xpath("//node[@text='{}']/@bounds".format(text))
    if elements:
        # 假设只找到一个元素，获取其坐标
        bounds = elements[0]
        left, top, right, bottom = eval(bounds.replace('][', ","))
        x = (left + right) // 2
        y = (top + bottom) // 2
        return [x, y]
    else:
        print("未发现element")
        return None


def find_current_element_num(xml_path, text):
    """
    从 XML 中根据文本数量
    :param xml_path: xml 地址
    :param text: 元素文本名称
    :return:
    """
    tree = html.etree.parse(xml_path)
    elements = tree.xpath("//node[@text='{}']/@bounds".format(text))
    if elements:
        return len(elements)
    else:
        print("未发现element")
        return None


def find_element_text(xml_path, text):
    """
    从 XML 中根据文本查找元素后面的文本，适用于查找订单号
    :param xml_path: xml 地址
    :param text: 元素文本名称
    :return:
    """
    tree = html.etree.parse(xml_path)
    elements = tree.xpath("//node[@text='{}']".format(text))
    print(elements)
    if elements:
        # 假设只找到一个元素，获取其坐标
        elements = tree.xpath("//node[@text='{}']/following-sibling::*[1]/@text".format(text))
        print(elements)
        if elements:
            # 假设只找到一个元素，获取其坐标
            text = elements[0]
        else:
            print("...")
            return None
        print(text)

        return text
    else:
        print("未发现element")
        return None


def find_current_element_text(xml_path, text):
    """
    从 XML 中根据文本查找当前元素的文本
    :param xml_path: xml 地址
    :param text: 元素文本名称
    :return:
    """
    tree = html.etree.parse(xml_path)
    print(text)
    print(tree.xpath("//node/@text"))
    elements = tree.xpath("//node[@text=$text]", text=text)
    print(elements)
    if elements:
        return True
    else:
        print("未发现element")
        return False


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

