def contains_only_y(input_str):
    # 将字符串转换为小写，并检测是否只包含字母 'y'
    return input_str.lower().isalpha() and all(
        char == "y" for char in input_str.lower()
    )


# 示例用法
test_str = "YyYyY"
result = contains_only_y(test_str)

if result:
    print(f"{test_str} 只包含字母 'y'")
else:
    print(f"{test_str} 不只包含字母 'y'")
