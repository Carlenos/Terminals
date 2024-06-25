hiragana = {"a": "あ", "i": "い", "u": "う", "e": "え", "o": "お",
            "ka": "か", "ki": "き", "ku": "く", "ke": "け", "ko": "こ",
            "ga": "が", "gi": "ぎ", "gu": "ぐ", "ge": "げ", "go": "ご",
            "sa": "さ", "shi": "し", "su": "す", "se": "せ", "so": "そ",
            "za": "ざ", "ji": "じ", "zu": "ず", "ze": "ぜ", "zo": "ぞ",
            "ta": "た", "chi": "ち", "tsu": "つ", "te": "て", "to": "と",
            "da": "だ", "zu": "づ", "de": "で", "do": "ど",
            "na": "な", "ni": "に", "nu": "ぬ", "ne": "ね", "no": "の",
            "ha": "は", "hi": "ひ", "fu": "ふ", "he": "へ", "ho": "ほ",
            "ba": "ば", "bi": "び", "bu": "ぶ", "be": "べ", "bo": "ぼ",
            "pa": "ぱ", "pi": "ぴ", "pu": "ぷ", "pe": "ぺ", "po": "ぽ",
            "ma": "ま", "mi": "み", "mu": "む", "me": "め", "mo": "も",
            "ya": "や", "yu": "ゆ", "yo": "よ",
            "ra": "ら", "ri": "り", "ru": "る", "re": "れ", "ro": "ろ",
            "wa": "わ", "wo": "を",
            "n": "ん",
            "kya": "きゃ", "kyu": "きゅ", "kyo": "きょ",
            "gya": "ぎゃ", "gyu": "ぎゅ", "gyo": "ぎょ",
            "sha": "しゃ", "shu": "しゅ", "sho": "しょ",
            "ja": "じゃ", "ju": "じゅ", "jo": "じょ",
            "cha": "ちゃ", "chu": "ちゅ", "cho": "ちょ",
            "nya": "にゃ", "nyu": "にゅ", "nyo": "にょ",
            "hya": "ひゃ", "hyu": "ひゅ", "hyo": "ひょ",
            "bya": "びゃ", "byu": "びゅ", "byo": "びょ",
            "pya": "ぴゃ", "pyu": "ぴゅ", "pyo": "ぴょ",
            "mya": "みゃ", "myu": "みゅ", "myo": "みょ",
            "rya": "りゃ", "ryu": "りゅ", "ryo": "りょ",
            "vu": "ゔ",
            "sakuon": "っ"}

katakana = {"a": "ア", "i": "イ", "u": "ウ", "e": "エ", "o": "オ",
            "ka": "カ", "ki": "キ", "ku": "ク", "ke": "ケ", "ko": "コ",
            "ga": "ガ", "gi": "ギ", "gu": "グ", "ge": "ゲ", "go": "ゴ",
            "sa": "サ", "shi": "シ", "su": "ス", "se": "セ", "so": "ソ",
            "za": "ザ", "ji": "ジ", "zu": "ズ", "ze": "ゼ", "zo": "ゾ",
            "ta": "タ", "chi": "チ", "tsu": "ツ", "te": "テ", "to": "ト",
            "da": "ダ", "zu": "ヅ", "de": "デ", "do": "ド",
            "na": "ナ", "ni": "ニ", "nu": "ヌ", "ne": "ネ", "no": "ノ",
            "ha": "ハ", "hi": "ヒ", "fu": "フ", "he": "ヘ", "ho": "ホ",
            "ba": "バ", "bi": "ビ", "bu": "ブ", "be": "ベ", "bo": "ボ",
            "pa": "パ", "pi": "ピ", "pu": "プ", "pe": "ペ", "po": "ポ",
            "ma": "マ", "mi": "ミ", "mu": "ム", "me": "メ", "mo": "モ",
            "ya": "ヤ", "yu": "ユ", "yo": "ヨ",
            "ra": "ラ", "ri": "リ", "ru": "ル", "re": "レ", "ro": "ロ",
            "wa": "ワ", "wo": "ヲ",
            "n": "ン",
            "kya": "キャ", "kyu": "キュ", "kyo": "キョ",
            "gya": "ギャ", "gyu": "ギュ", "gyo": "ギョ",
            "sha": "シャ", "shu": "シュ", "sho": "ショ",
            "ja": "ジャ", "ju": "ジュ", "jo": "ジョ",
            "cha": "チャ", "chu": "チュ", "cho": "チョ",
            "nya": "ニャ", "nyu": "ニュ", "nyo": "ニョ",
            "hya": "ヒャ", "hyu": "ヒュ", "hyo": "ヒョ",
            "bya": "ビャ", "byu": "ビュ", "byo": "ビョ",
            "pya": "ピャ", "pyu": "ピュ", "pyo": "ピョ",
            "mya": "ミャ", "myu": "ミュ", "myo": "ミョ",
            "rya": "リャ", "ryu": "リュ", "ryo": "リョ",
            "vu": "ヴ",
            "va": "ヴァ", "vi": "ヴィ", "ve": "ヴェ", "vo": "ヴォ",
            "wi": "ウィ", "we": "ウェ",
            "fa": "ファ", "fi": "フィ", "fe": "フェ", "fo": "フォ",
            "che": "チェ",
            "di": "ディ", "du": "ドゥ",
            "ti": "ティ", "tu": "トゥ",
            "je": "ジェ",
            "she": "シェ",
            "sakuon": "ッ",
            "pause": "ー"}


def romajiToJapanese(romaji):
    romaji = romaji.lower()
    current_alphabet = hiragana
    hiragana_is_current = True
    result_str = ""
    i = 0
    while i < len(romaji):
        if romaji[i] == "*":  # switch alphabets
            if hiragana_is_current:
                current_alphabet = katakana
                hiragana_is_current = False
            else:
                current_alphabet = hiragana
                hiragana_is_current = True
            i += 1
        elif romaji[i] == " ":  # check wa rule
            if i + 3 < len(romaji):
                if romaji[i:i + 4] == " wa ":  # ha/wa rule
                    result_str += " %s " % current_alphabet["ha"]
                    i += 4
                    continue
            result_str += " "
            i += 1
        elif i + 2 < len(romaji) and romaji[i] == "n" and romaji[i + 1:i + 2] == "n" and romaji[
                                                                                         i + 1:i + 3] not in current_alphabet:  # n rule
            result_str += current_alphabet["sakuon"]
            i += 1
        else:
            check_len = min(3, len(romaji) - i)
            while check_len > 0:
                check_str = romaji[i:i + check_len]
                if check_str in current_alphabet:
                    result_str += current_alphabet[check_str]
                    i += check_len
                    if i < len(romaji):
                        if romaji[i] == "o" and romaji[i - 1:i] == "o" and hiragana_is_current:  # oo = ou rule
                            result_str += current_alphabet["u"]
                            i += 1
                        elif romaji[i] == "e" and romaji[i - 1:i] == "e" and hiragana_is_current:  # ee = ei rule
                            result_str += current_alphabet["i"]
                            i += 1
                        elif romaji[i] == romaji[i - 1:i] and hiragana_is_current == False:
                            if romaji[i] == "n":
                                break
                            elif romaji[i] in ["a", "e", "i", "o", "u"]:
                                result_str += current_alphabet["pause"]
                            else:
                                result_str += current_alphabet["sakuon"]
                            i += 1
                    break
                elif check_len == 1:
                    if check_str == "?" or check_str == "." or check_str == "!":  # punctuation
                        result_str += "。"
                    elif check_str not in ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o",
                                           "p", "q", "r", "s", "t", "u", "v", "w", "x", "y",
                                           "z"]:  # print any characters that aren't a letter
                        result_str += check_str
                    elif i + 1 < len(romaji):  # little tsu rule
                        if check_str == romaji[i + 1:i + 2]:
                            result_str += current_alphabet["sakuon"]
                    i += 1
                    break
                check_len -= 1
    return result_str
