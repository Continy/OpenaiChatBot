import os
import openai
from graia.ariadne.app import Ariadne
from graia.ariadne.entry import config
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.model import Friend
from graia.ariadne.model import Group
from graia.ariadne.message.parser.base import *

openai.api_key = os.getenv("OPENAI_API_KEY")
QQnum = os.getenv("OPENAI_BOT_NUM")
chatMode = 0
askSet = []
ansSet = []
settingSet = ''


def generateInput(askSet, ansSet, settingSet):
    output = settingSet + '\n'
    for i in range(0, len(askSet) - 1):
        output = output + 'User: ' + askSet[i] + '\n' + 'AI: ' + ansSet[
            i] + '\n'
    output = output + 'User: ' + askSet[-1] + '\n' + 'AI: '
    return output


app = Ariadne(
    config(
        verify_key="12345678",  # 填入 VerifyKey
        account=int(QQnum),  # 你的机器人的m  qq 号
    ), )


@app.broadcast.receiver("FriendMessage", decorators=[MentionMe()])
async def friend_message_listener(app: Ariadne, friend: Friend,
                                  message: MessageChain):
    print(message)
    # 实际上 MessageChain(...) 有没有 "[]" 都没关系


@app.broadcast.receiver("GroupMessage")
async def group_message_listener(app: Ariadne, group: Group,
                                 message: MessageChain):
    global chatMode
    global askSet
    global ansSet
    global settingSet
    print(message.display)
    at_1 = [r.span() for r in re.finditer('@3475', message.display)]
    at_2 = [r.span() for r in re.finditer('Bot', message.display)]
    print(at_2)
    if at_1 or at_2:
        if at_1:
            message = message.display[11:]
        else:
            message = message.display[14:]
        img_index = [r.span() for r in re.finditer('生成', message)]
        chat_index = [r.span() for r in re.finditer('/chat', message)]
        print(img_index)
        #await app.send_message(Group, MessageChain([Plain("别急，停机维护中")]))
        if chat_index:
            if chatMode:
                chatMode = 0
                askSet = []
                ansSet = []
                settingSet = ''
                await app.send_message(group,
                                       MessageChain([Plain('chatMode = 0')]))
            else:
                chatMode = 1
                settingSet = message[6:]
                await app.send_message(
                    group, MessageChain([Plain('chatMode = 1 ' + settingSet)]))

        elif img_index:
            inputStr = message[3:]
            print(inputStr)
            # response = openai.Image.create(prompt=inputStr, n=1, size="256x256")
            # image_url = response['data'][0]['url']
            # await app.send_message(group, MessageChain([Plain(image_url)]))

        else:
            print("#######################")
            if chatMode:
                askSet.append(message)
                print(generateInput(askSet, ansSet, settingSet))
                response = openai.Completion.create(model="text-davinci-003",
                                                    prompt=generateInput(
                                                        askSet, ansSet,
                                                        settingSet),
                                                    temperature=0.9,
                                                    max_tokens=300,
                                                    top_p=1,
                                                    frequency_penalty=0,
                                                    presence_penalty=0.6)
                result = response['choices'][0]['text']
                ansSet.append(result)
                await app.send_message(group, MessageChain([Plain(result)]))
            else:
                response = openai.Completion.create(model="text-davinci-003",
                                                    prompt=message,
                                                    temperature=0.3,
                                                    max_tokens=1024,
                                                    top_p=1,
                                                    frequency_penalty=0,
                                                    presence_penalty=0)
                result = response['choices'][0]['text']
                all_index = [r.span() for r in re.finditer('\n', result)]
                await app.send_message(
                    group, MessageChain([Plain(result[all_index[1][1]:])]))


app.launch_blocking()
