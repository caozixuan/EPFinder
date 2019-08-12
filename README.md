# EPFinder User Manual

## 1. Compare code pairs

`detect_pair(code1, code2)`

`code1` and `code2` is the the string representation of codes.

    from EPFiner.compare import detect_pair
    code1 = ""    # read code content from files
    code2 = ""    # read code content from files
    print(detect_pair(code1,code2)) 

## 2. Compare within directory

`detect_directory(root, number, th)`

`root` is the source directory of all codes that need to be detected.
`number` is the number of clustering centers.
`th` is the similarity threshold. Similarity larger than th will be print.

    from EPFiner.compare import detect_directory
    detect_directory('C:\\codes', 4, 0.7)

## 3. Compare codes with labels

`detect_content(notes,codes,number,th)`

`notes` is the labels that each code has. For example, `notes = ['Tom','Jerry','Mike']` means the code in codes
belongs to Tom, Jerry, Mike separately.
`codes` is an array that contents all codes.
`number` is the number of clustering centers.
`th` is the similarity threshold. Similarity larger than th will be print.


    from EPFiner.compare import detect_content
    code1 = ""    # read code content from files
    code2 = ""    # read code content from files
    cpde3 = ""    # read code content from files
    notes = ['Tom','Jerry','Mike']
    codes = [code1, code2, code3]
    detect_content(notes, codes, 4, 0.5)
