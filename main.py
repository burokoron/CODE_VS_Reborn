#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import sys
import copy
from operator import mul

AI_NAME = "burokoron_v0.53"
width = 10
height = 16
packSize = 2
summation = 20
maxTurn = 500
simulationHeight = height + packSize + 1
OBSTACLE_BLOCK = summation + 1
EMPTY_BLOCK = 0
packs = []


# 標準入力からパックを得ます
def inputPack():
    pack = [[int(i) for i in input().split()] for j in range(packSize)]
    input()  # END
    return pack


# パックを90度回転させます
def rotateOnce(pack):
    rotated = copy.deepcopy(pack)
    for i in range(packSize):
        for j in range(packSize):
            rotated[j][packSize - 1 - i] = pack[i][j]
    return rotated


# パックを指定した回数だけ90度回転させます
def rotate(pack, rotation):
    for _ in range(rotation):
        pack = rotateOnce(pack)
    return pack


# パックの落下およびブロック消滅処理
def update_field(field):
    count = 0
    while(True):
        mask = [width*[1] for i in range(simulationHeight)]

        # 消滅するブロックを数える
        for j in range(width-1, -1, -1):
            for i in range(simulationHeight-1, simulationHeight-height-2, -1):
                if((field[i][j]+field[i-1][j]) == 10):
                    mask[i][j] = 0
                    mask[i-1][j] = 0
                if(j != 0):
                    if((field[i][j]+field[i][j-1]) == 10):
                        mask[i][j] = 0
                        mask[i][j-1] = 0
                    if((field[i][j]+field[i-1][j-1]) == 10):
                        mask[i][j] = 0
                        mask[i-1][j-1] = 0
                if(j != width-1):
                    if((field[i][j]+field[i-1][j+1]) == 10):
                        mask[i][j] = 0
                        mask[i-1][j+1] = 0

        if(sum(map(sum, mask)) == width*simulationHeight): break
        else: count += 1

        # ブロックを消滅させる
        field = list(map(lambda x,y: list(map(lambda a,b: a*b, x,y)), field,mask))

        # ブロックの落下
        for j in range(width-1, -1, -1):
            for i in range(simulationHeight-1, 0, -1):
                if(field[i][j] != EMPTY_BLOCK): continue

                upblock = 0
                for k in range(i-1, -1, -1):
                    if(field[k][j] == EMPTY_BLOCK): continue

                    upblock = i - k
                    break
                
                for k in range(i, upblock, -1):
                    field[k][j] = field[k-upblock][j]
                    if(field[k][j] == EMPTY_BLOCK): break


    return (count, field)
    

def evaluate(myfield, mypack, move, v, skill):
    for j in range(2):
        for i in reversed(range(simulationHeight)):
            if myfield[i][move[1]+j] == EMPTY_BLOCK:
                if(mypack[1][j] == 0): myfield[i][move[1]+j] = mypack[0][j]
                else:
                    myfield[i][move[1]+j] = mypack[1][j]
                    myfield[i-1][move[1]+j] = mypack[0][j]
                break

    # ブロックの消滅
    count, myfield = update_field(myfield)

    if(sum(myfield[simulationHeight-height-1]) != 0):
        return [-9999, move, myfield, skill]

    height_count = []
    for i in range(width): height_count.append(list(map(lambda x: x[i], myfield)).count(0))
    v += (min(height_count) - max(height_count)) * 10



    for j in range(width-1, -1, -1):
        for i in range(simulationHeight-1, simulationHeight-height-2, -1):
            if(myfield[i][j] != EMPTY_BLOCK and myfield[i][j] != OBSTACLE_BLOCK): v += 1

            
            if(myfield[i][j] == 5):
                if(j == width-1 or j == 0 or i == simulationHeight-1): v += 30
                else: v += 60

            bom = 0
            emp = 0
            obs = 0
            if(j == width-1 and i == simulationHeight-1):
                for k in list(map(lambda x: x[j-1:j+1], myfield[i-1:i+1])):
                    bom += k.count(5)
                    emp += k.count(EMPTY_BLOCK)
                    obs += k.count(OBSTACLE_BLOCK)
                if(bom != 0): v += 4 - obs*5 - emp - bom*2
                elif(emp != 0): v -= 1
            if(j == 0 and i == simulationHeight-1):
                for k in list(map(lambda x: x[j:j+2], myfield[i-1:i+1])):
                    bom += k.count(5)
                    emp += k.count(EMPTY_BLOCK)
                    obs += k.count(OBSTACLE_BLOCK)
                if(bom != 0): v += 4 - obs*5 - emp - bom*2
                elif(emp != 0): v -= 1
            if(j == width-1):
                for k in list(map(lambda x: x[j-1:j+1], myfield[i-1:i+2])):
                    bom += k.count(5)
                    emp += k.count(EMPTY_BLOCK)
                    obs += k.count(OBSTACLE_BLOCK)
                if(bom != 0): v += 6 - obs*5 - emp - bom*2
                elif(emp != 0): v -= 1
            elif(j == 0):
                for k in list(map(lambda x: x[j:j+2], myfield[i-1:i+2])):
                    bom += k.count(5)
                    emp += k.count(EMPTY_BLOCK)
                    obs += k.count(OBSTACLE_BLOCK)
                if(bom != 0): v += 6 - obs*5 - emp - bom*2
                elif(emp != 0): v -= 1
            elif(i == simulationHeight-1):
                for k in list(map(lambda x: x[j-1:j+2], myfield[i-1:i+1])):
                    bom += k.count(5)
                    emp += k.count(EMPTY_BLOCK)
                    obs += k.count(OBSTACLE_BLOCK)
                if(bom != 0): v += 6 - obs*5 - emp - bom*2
                elif(emp != 0): v -= 1
            else:
                for k in list(map(lambda x: x[j-1:j+2], myfield[i-1:i+2])):
                    bom += k.count(5)
                    emp += k.count(EMPTY_BLOCK)
                    obs += k.count(OBSTACLE_BLOCK)
                if(bom != 0): v += 9 - obs*5 - emp - bom*2
                elif(emp != 0): v -= 1
                
            if(myfield[i][j] != 5):
                if(j != width-1):
                    if((myfield[i][j]+myfield[i-2][j-1]) == 10 or (myfield[i][j]+myfield[i-2][j+1]) == 10): v -= 1
                elif((myfield[i][j]+myfield[i-2][j-1]) == 10): v -= 1


    if(count != 0):
        if(skill >= 100):
            skill = 100
        else:
            skill += 8
            v += 100 - skill
            if(v > 1000): v += 300


    return [v//2, move, myfield, skill]
    

# 探索
def search(field, skill, packs, turn, obstacleCount, depth):
    move_list = []
    for i in range(4):
        for j in range(9):
            move_list.append([i, j])

    value = -9999
    best_move = [0, 0]
    beam_list = []
    field, obstacleCount = fallObstacle(field, obstacleCount)

    # 1手目の探索
    for move in move_list:
        myfield = copy.deepcopy(field)
        mypack = rotate(packs[turn], move[0])

        tmp = evaluate(myfield, mypack, move, 0, skill)
        beam_list.append([tmp[0], move, tmp[2], tmp[3], obstacleCount])

    
    # 2手目以降の探索(ビームサーチ)
    for i in range(depth):
        tmp_list = sorted(beam_list)[::-1][:10]
        if(tmp_list[0][0] == -9999): break
        beam_list = []

        for status in tmp_list:
            for move in move_list:
                if(status[0] == -9999): continue
                v = status[0]
                myfield = copy.deepcopy(status[2])
                mypack = rotate(packs[turn+i+1], move[0])
                skill = status[3]
                obstacleCount = status[4]
                myfield, obstacleCount = fallObstacle(myfield, obstacleCount)

                tmp = evaluate(myfield, mypack, move, v, skill)
                beam_list.append([tmp[0], status[1], tmp[2], tmp[3], obstacleCount])
    
    beam_list = sorted(beam_list)[::-1]
    #for i in beam_list:
    #    print(i[0], i[1])

    return (beam_list[0][1], beam_list[0][0])


# 標準エラー出力にパックの情報を出力します
def printPack(pack):
    print('\n'.join(map(lambda row: ' '.join(map(lambda block: '{:>2}'.format(block), row)), pack)), file=sys.stderr)
    sys.stdout.flush()


# 標準入力から盤面を得ます
def inputField():
    field = [[EMPTY_BLOCK] * width if j < simulationHeight - height else [int(i) for i in input().split()]
             for j in range(simulationHeight)]
    input()  # END
    return field


# def alternativeInputField():
#    field = []
#    for j in range(simulationHeight):
#        if j < simulationHeight - height:
#            row = []
#            for i in range(width):
#                row.append(EMPTY_BLOCK)
#            field.append(row)
#        else:
#            row = []
#            temp = input().split()
#            for i in range(width):
#                row.append(int(temp[i]))
#            field.append(row)
#    end = input()
#    return field

# お邪魔カウントに応じて、盤面にお邪魔ブロックを落とします
def fallObstacle(field, obstacleCount):
    after = copy.deepcopy(field)
    if obstacleCount < width:
        return (after, obstacleCount)
    for j in range(width):
        for i in reversed(range(simulationHeight)):
            if field[i][j] == EMPTY_BLOCK:
                field[i][j] = OBSTACLE_BLOCK
                break
    return (after, obstacleCount-width)


# 標準エラー出力に盤面の情報を出力します
def printField(field):
    print('\n'.join(map(lambda row: ' '.join(map(lambda block: '{:>2}'.format(block), row)), field)), file=sys.stderr)
    sys.stdout.flush()


def main():
    # AIの名前を出力する
    print(AI_NAME)
    sys.stdout.flush()
    random.seed(123456)

    # ゲーム情報の取得
    for _ in range(maxTurn):
        packs.append(inputPack())

    # ターンの処理
    try:
        while True:
            # 1ターン分のデータを受け取る
            turn = int(input())

            millitime = int(input())
            obstacleCount = int(input())
            skill = int(input())
            score = int(input())
            field = inputField()

            enemyMillitime = int(input())
            enemyObstacleCount = int(input())
            enemySkill = int(input())
            enemyScore = int(input())
            enemyField = inputField()
            enemyField, enemyObstacleCount = fallObstacle(enemyField, enemyObstacleCount)

            # 操作を決定する
            pack = packs[turn]
            depth = 3
            move, value = search(field, skill, packs, turn, obstacleCount, depth)

            #print("turn: " + str(turn), file=sys.stderr)
            #printPack(pack)
            #printField(field)
            
            # 出力する
            height_count = []
            for i in range(width): height_count.append(list(map(lambda x: x[i], enemyField)).count(0))
            height_count = int(min(height_count)*0.75+max(height_count)*0.25)
            if(skill >= 80 and (value >= height_count*100 or value == -9999 or obstacleCount >= 10)): print("S")
            else: print(move[1], move[0])
            print(move, value, skill, height_count, file=sys.stderr)
            sys.stdout.flush()

    except Exception as e:
        print("error: {0}".format(e), file=sys.stderr)


if __name__ == '__main__':
    main()
