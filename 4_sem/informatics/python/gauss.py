# Теперь декодируем вторую часть: "--...-.-.-."
s2 = "--...-.-.-."
N2 = len(s2)

decodings_s2 = []

def backtrack2(index, current_decoding):
    if index == N2:
        decodings_s2.append("".join(current_decoding))
        return
    for i in range(index+1, N2+1):
        prefix = s2[index:i]
        if prefix in morse_dict:
            current_decoding.append(morse_dict[prefix])
            backtrack2(i, current_decoding)
            current_decoding.pop()

backtrack2(0, [])
decodings_s2
