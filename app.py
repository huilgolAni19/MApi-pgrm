import difflib
import pandas as pd
import json
from flask import Flask, request, jsonify
import base64

app = Flask(__name__)

file_name = "words.txt"

data = pd.read_csv(file_name, sep=" ", header=None , names=["keyword"])
mdata= data.keyword.astype(str)


# Request Body String {"QueryWord":"appel", "Token":"VG9rZW4tMQ=="}
@app.route('/checkspell/api/v1/', methods=['POST'])
def api_v1_check_spelling():
    request_json = request.json
    queryWord = request_json["QueryWord"]
    currentToken = request_json["Token"]
    #print("currentToken: {}".format(currentToken))
    tkn = base64.b64decode(currentToken.encode('utf-8'))
    mtkn = tkn.decode("utf-8")
    #print("Str Tkn: {}".format(mtkn))
    result = checkSpelling(queryWord, mtkn)
    return jsonify(result)

# This is for check
def checkSpelling(given_word, currentToken):
    json_result = {}
    result_array = []
    nextToken = generateNextToken(currentToken)
    print("This Will Be The Next Token: {}".format(nextToken))
    array = difflib.get_close_matches(given_word.lower(), mdata, n=(len(mdata) + 1), cutoff = .819)

    json_result["Status"] = "Success"
    json_result["QueryWord"] = given_word
    json_result["NextToken"] = generateNextToken(currentToken) #currentToken #generateNextToken(currentToken)
    if len(array) > 0 :
        json_result["MatchFoundCount"] = len(array)
        for item in array:
            itemObj = {}
            score = difflib.SequenceMatcher(None, given_word.lower(), item).ratio()
            socre_two_decimal = "{:.5f}".format(score)
            itemObj["CloseMatch"] = item
            itemObj["Confidance"] = float(socre_two_decimal)
            result_array.append(itemObj)
    else:
        json_result["MatchFoundCount"] = len(array)
    json_result["Result"] = result_array
    return json_result

def generateNextToken(thisToken):
    array_str = thisToken.split("-")
    tkn_cnt = int(array_str[1])
    tkn_cnt += 1
    tkn_str = "{}-{}".format(array_str[0], tkn_cnt);
    #print("Next Token {}".format(tkn_str))
    token = base64.b64encode(bytes(u'{}'.format(tkn_str), "utf-8"))
    #print(type(token))
    dtkn = token.decode("utf-8")
    return dtkn

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
