import pandas as pd
import re
import CaboCha
import unicodedata
import MeCab

df_kaken = pd.read_excel("/Users/yumoto/my_dev/kaken/data/materials.xlsx")
df_gimrt = pd.read_csv("../data/GIMRT課題/GIMRT_2020.txt", sep="\t")


m = MeCab.Tagger("-Ochasen -r /usr/local/etc/mecabrc")
# m = MeCab.Tagger("-r /usr/local/etc/mecabrc")
# CaboChaへの入力
#    全角記号を前提とするため、丸括弧と！は全角記号に戻す。
translation_table = str.maketrans(dict(zip("()!", "（）！")))
cp = CaboCha.Parser()  # パーサーを得る


def textCleansing(text):
    """
    変更
    unicodedataのnormalize関数によって文字の表記を統一する。
        半角カタカナ→全角カタカナ
        全角英字→半角英字
        全角記号→半角記号
        全角空白記号→半角空白記号
    ２つ以上の空白記号が日本語文字列に混ざると問題になるので、１つにする。
    """
    text = text
    text = unicodedata.normalize("NFKC", text).translate(translation_table)
    text = re.sub(r"\s+", " ", text)
    return text


def mkWordBodyList(text):
    rlist = []
    xlist = [u.split() for u in m.parse(text).splitlines()]
    # print(xlist)
    for i in xlist:
        # print(i)
        if len(i) < 2:
            pass
        else:
            if "固有名詞" in i[-1] or "名詞-一般" in i[-1]:
                # print(i[0])
                rlist.append(i[0])
    return rlist


def gen_chunks(tree):
    """
    構文木treeからチャンクの辞書を生成する
    """
    chunks = {}
    key = 0  # intにしているがこれはChunk.linkの値で辿れるようにしている

    for i in range(tree.size()):  # ツリーのサイズだけ回す
        tok = tree.token(i)  # トークンを得る
        if tok.chunk:  # トークンがチャンクを持っていたら
            chunks[key] = tok.chunk  # チャンクを辞書に追加する
            key += 1

    return chunks


def get_surface(tree, chunk):
    """
    chunkからtree内のトークンを得て、そのトークンが持つ表層形を取得する
    """
    surface = ""
    beg = chunk.token_pos  # このチャンクのツリー内のトークンの位置
    end = chunk.token_pos + chunk.token_size  # トークン列のサイズ

    for i in range(beg, end):
        token = tree.token(i)
        surface += token.surface  # 表層形の取得

    return surface


def getsfce(text):
    sentence = "猫は道路を渡る犬を見た。"
    sentence = text

    # cp = CaboCha.Parser()  # パーサーを得る
    tree = cp.parse(sentence)  # 入力から構文木を生成

    # print(tree.toString(CaboCha.FORMAT_TREE))  # デバッグ用

    chunks = gen_chunks(tree)  # チャンクの辞書を生成する

    surfaces = []
    to_surfaces = ["dummy"]
    for from_chunk in chunks.values():
        if from_chunk.link < 0:
            continue  # リンクのないチャンクは飛ばす

        # このチャンクの表層形を取得
        from_surface = get_surface(tree, from_chunk)

        # from_chunkがリンクしているチャンクを取得
        to_chunk = chunks[from_chunk.link]
        to_surface = get_surface(tree, to_chunk)

        # 出力
        # print(from_surface, "->", to_surface)
        print(from_surface)
        surfaces.append(from_surface)
        surfaces.append(to_surface)
        to_surfaces.append(to_surface)
    if len(to_surfaces) > 0:
        print(to_surfaces[-1])
    surfaces = sorted(set(surfaces))
    return surfaces


def main():
    titles = []
    for i in df_kaken["研究課題名"]:
        titles.append(i)
    for i in df_gimrt["課題名"]:
        i = textCleansing(i)
        titles.append(i)

    wordbodylist = []
    wordbodylistE = []

    for i in titles:
        # print(i)
        i = str(i)
        if len(i) < 2:
            i = "non"
        nounlist = mkWordBodyList(i)

        for j in nounlist:
            if re.match(r"^[a-zA-Z]+?$", j):
                wordbodylistE.append(j)
            else:
                wordbodylist.append(j)

    wordbodylist = sorted(set(wordbodylist))
    wordbodylistE = sorted(set(wordbodylistE))
    outxt = "\n".join(wordbodylist)
    with open("../result/用語確認.txt", "w") as f:
        f.write(outxt)

    chk = 0
    kakuninhyosokei = []
    for i in range(len(titles)):
        if str(titles[i]) == "nan":
            pass
        else:
            print("\n" + "===================")
            print(str(chk) + ": " + titles[i])
            tmplist = getsfce(titles[i])
            nounlist = mkWordBodyList(titles[i])
            print(nounlist)
            chk += 1

        for j in tmplist:
            kakuninhyosokei.append(j)

    kakuninhyosokei = sorted(set(kakuninhyosokei))
    tmptxtline = "\n".join(kakuninhyosokei)
    with open("../result/用語確認2.txt", "w") as f:
        f.write(tmptxtline)


main()
