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


def addSetting(new):
    global settingSet
    settingSet = settingSet + '\n' + new


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

    at_1 = [r.span() for r in re.finditer('@3475', message.display)]
    at_2 = [r.span() for r in re.finditer('Bot', message.display)]

    if at_1 or at_2:
        if at_1:
            message = message.display[11:]
        else:
            message = message.display[4:]
        img_index = [r.span() for r in re.finditer('生成', message)]
        chat_index = [r.span() for r in re.finditer('-', message)]
        #await app.send_message(Group, MessageChain([Plain("别急，停机维护中")]))
        if chat_index:
            mode1 = [r.span() for r in re.finditer('1', message)]
            modeAdd = [r.span() for r in re.finditer('add', message)]
            mode0 = [r.span() for r in re.finditer('0', message)]
            if chatMode and mode0:
                chatMode = 0
                askSet = []
                ansSet = []
                settingSet = ''
                await app.send_message(group, MessageChain([Plain('-0')]))
            elif mode1:
                chatMode = 1
                settingSet = message[2:]
                await app.send_message(
                    group, MessageChain([Plain('-1' + settingSet)]))
            elif modeAdd:
                chatMode = 1
                settingSet = message[4:]
                addSetting(settingSet)
                await app.send_message(
                    group, MessageChain([Plain('-add' + settingSet)]))

        elif img_index:
            inputStr = message[3:]
            response = openai.Image.create(prompt=inputStr,
                                           n=1,
                                           size="512x512")
            image_url = response['data'][0]['url']
            await app.send_message(group, MessageChain([Plain(image_url)]))

        # else:
        #     print("#######################")
        # if chatMode:
        #     askSet.append(message)
        #     print(generateInput(askSet, ansSet, settingSet))
        #     response = openai.Completion.create(model="text-davinci-003",
        #                                         prompt=generateInput(
        #                                             askSet, ansSet,
        #                                             settingSet),
        #                                         temperature=0.9,
        #                                         max_tokens=150,
        #                                         top_p=1,
        #                                         frequency_penalty=0,
        #                                         presence_penalty=0.6)
        #     result = response['choices'][0]['text']
        #     ansSet.append(result)
        #     await app.send_message(group, MessageChain([Plain(result)]))
        else:
            try:
                response = openai.Completion.create(model="text-davinci-003",
                                                    prompt=message,
                                                    temperature=0.3,
                                                    max_tokens=250,
                                                    top_p=1,
                                                    frequency_penalty=0,
                                                    presence_penalty=0)
                result = response['choices'][0]['text']
                all_index = [r.span() for r in re.finditer('\n', result)]
                await app.send_message(
                    group, MessageChain([Plain(result[all_index[1][1]:])]))
            except:
                await app.send_message(group,
                                       MessageChain([Plain("什么情况？死机了！")]))


app.launch_blocking()
