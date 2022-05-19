if __name__ == '__main__':
    num = str(3)
    file_path = 'E:/bft_testing/Test_twins_with_oopsla/logs/round-'+num+'-generate-states-num.log'
    file1 = open(file_path, 'r', encoding='utf-8')
    # 打开文件love.txt
    file_content = file1.readlines()[4:]
    lines = sorted(file_content, key=lambda x: len(x))
    # 读取文件，我们需要将读取到的内容放入变量中，这样才能拿到文件内容
    new_file_path = 'E:/bft_testing/Test_twins_with_oopsla/logs/'+num+'.log'
    with open(new_file_path, 'w') as f:
        f.write(''.join(lines))
