# -*- coding: utf8
import os
import socket
import sys
from json import JSONEncoder

import datetime

reload(sys)
sys.setdefaultencoding("utf-8")
# 2017/3/23 10:15
__author__ = 'haizhu'

import math
import time

# all(0, AppVer.VER_LATEST, "post"), // 这个是获取的时候使用，如果是all
# 全部都获取出来，为以后朋友圈预留
# images(1, AppVer.VER_INIT, "照片"), // 相册post
# mood(2, AppVer.VER_INIT, "心情"), // 心情post
# text(3, AppVer.VER_INIT, "文本"), // 纯文字
# forward(4, AppVer.VER_INIT, "转发"), // 转发.只会影响newfeed
# userInfo(5, AppVer.VER_1_2_70, "新鲜事"), // 用户修改信息以及生日发布的post
# interest(6, AppVer.VER_1_2_70, "兴趣"), // 兴趣
# superInterest(7, AppVer.VER_1_2_70, "超级兴趣"), // 超级兴趣
# video(8, AppVer.VER_1_2_70, "视频"), // 视频
# song(9, AppVer.VER_1_2_80, "音乐"), // 歌曲
# blog(10, AppVer.VER_1_2_80, "日志"), // 日志
# customVideo(11, AppVer.VER_1_3_10, "视频"), // 新的视频类型

##每个post类型对应的权值
POST_TYPE_SCORE = {1: 1.,
                   2: 1.2,
                   3: 1,
                   4: 0,
                   5: 0,
                   6: 0,
                   7: 0,
                   8: 2.2,
                   9: 1.6,
                   10: 22.,
                   11: 1.8}

# 每个操作对应的基础值
POST_FORWORD_BASE_SCORE = 4.0;
POST_COMMENT_BASE_SCORE = 2.0
POST_FAV_BASE_SCORE = 1.0

# 是否打印中间信息
PRINT_INFO = False


# pv影响影响因子 例如pv越大数值越可靠 范围[50,100]
def pvCountFactor(currentPVCount, maxPVCount):
    # print currentPVCount, maxPVCount
    # y = (1 + sin(π * ((x - 2500) / 5000)))
    return 100 * ((1 + math.sin(math.pi * ((currentPVCount * 1.) / maxPVCount - 0.5))) / 2)


# 时间降序因子 【0，3]天，换算成分钟[0,3*24*60]
MAX_MINU = 3 * 24 * 60.


def timeDescFactor(currentTime):
    # (cos(x * π / 168) + 1) / 2
    if MAX_MINU <= currentTime:
        return 0
    return 100 * ((math.cos(currentTime * math.pi / MAX_MINU) + 1) / 2)


def readPVLog(baseDir, postCountLog):
    # # 开始计算权值
    f = open(postCountLog)
    line = f.readline()
    post_score = {}
    forword_post_scores = {}

    current_secords = time.time()

    post_create_times = {}

    while line:
        line = line.strip()
        bases = line.split(" ")
        line = f.readline().strip()
        if len(bases) == 7:
            postId = (bases[0])
            orgId = (bases[1])

            create_time = long(bases[2])

            forword_count = int(bases[3])
            fav_count = int(bases[4])
            commend_count = int(bases[5])
            commend_user_count = int(bases[6])
            score = forword_count * POST_FORWORD_BASE_SCORE \
                    + fav_count * POST_FAV_BASE_SCORE \
                    + (commend_user_count + (
                commend_count - commend_user_count) / 10) * POST_COMMENT_BASE_SCORE  # 相同的人评论10条算一个
            if score <= 0:
                continue

            if orgId != "0":
                # 转发的，算到源post里面
                if forword_post_scores.has_key(orgId):
                    forword_post_scores[orgId] += score;
                else:
                    forword_post_scores[orgId] = score;
                continue

            post_create_times[postId] = (current_secords - create_time / 1000) / 60.
            if post_score.has_key(postId):
                post_score[postId] += score
            else:
                post_score[postId] = score
    f.close()
    print "权值求和计算完成，共计", len(post_score), "条记录满足要求"
    # 权值求和计算完成

    # 求每个用户的权值和
    pv_counts = {};
    post_types = {}
    max_pv_count = 1;
    for postPVLog in os.listdir(baseDir):
        f = open(os.path.join(baseDir, postPVLog))

        if postPVLog.startswith("."):
            print "skip file ", f.name
            continue
        print "read file ", f.name

        line = f.readline().strip()
        while line:
            bases = line.split("|")
            line = f.readline().strip()
            if len(bases) == 2:
                datas = bases[1].split(" ")
                postId = (datas[0])
                if post_score.has_key(postId):
                    postType = int(datas[1])
                    post_types[postId] = postType
                    if pv_counts.has_key(postId):
                        cpv = pv_counts[postId] + 1;
                        pv_counts[postId] = cpv;
                        if cpv > max_pv_count:
                            max_pv_count = cpv;

                    else:
                        pv_counts[postId] = 1
        f.close()

    print max_pv_count
    count = 0;
    if PRINT_INFO:
        print "|PV排名|postId|PV|"
        print "|-|-|-|"
        for k, v in sorted(pv_counts.items(), lambda x, y: cmp(x[1], y[1]), reverse=True):
            if count > 200:
                break
            count += 1;
            print "|", count, "|", "[" + k + "](https://sol.jiemosrc.com/post/search/byIDorUUID?postId=" + k + ")", "|", v, "|"

    # 开始求权值排名
    score_result = {}
    if PRINT_INFO:
        print "\n|权值求和|postId|score|"
        print "|-|-|-|"
        count = 0;

    for k, v in sorted(post_score.items(), lambda x, y: cmp(x[1], y[1]), reverse=True):
        if v >= 20.0 and pv_counts.has_key(k):
            pvc = pv_counts[k]
            if pvc < 100:
                continue

            if forword_post_scores.has_key(k):  # 如果有转发的权值  也加到源post里面
                v += forword_post_scores[k]
            score_result[k] = timeDescFactor(post_create_times[k]) * pvCountFactor(currentPVCount=pvc,
                                                                                   maxPVCount=max_pv_count) * v / pvc
            if PRINT_INFO:
                count += 1
                print "|", count, "|", k, "|", v, "|"

    if True:
        score_result = sorted(score_result.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
        count = 0;
        print "\n|计算后权值排名|postId|score|pv|totalScore|pvRate|timeDesRate|postType|"
        print "|-|-|-|-|-|-|-|-|"
        for k, v in score_result:
            count += 1
            # if post_types[k] != 10:
            #     continue
            print "|", count, "|", "[" + k + "](https://sol.jiemosrc.com/post/search/byIDorUUID?postId=" + k + ")", "|", v, "|", \
                pv_counts[k], "|", post_score[k], "|", \
                pvCountFactor(currentPVCount=pv_counts[k], maxPVCount=max_pv_count), "|", \
                timeDescFactor(post_create_times[k]), "|", post_types[k], "|"
            # if count > 500:
            #     break
    return score_result


if __name__ == '__main__':

    s = datetime.datetime.now()
    args_lg = len(sys.argv)

    baseDir = "/Users/haizhu/Downloads/result/result/postPV";

    # 是否是外网
    if True:
        now = datetime.datetime.now()
        # host = "search.d.jiemoapp.com"
        host = "cluster.d.jiemoapp.com"

        baseDir = "/data/postPV"

        # os.system("rm -rf " + baseDir)
        if not os.path.exists(baseDir):
            os.makedirs(baseDir)

        currentIP = os.popen("ifconfig").read()

        hasFile = True
        postPVFiles = []

        for info in socket.getaddrinfo(host, 80, socket.AF_UNSPEC,
                                       socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
            ip = str(info[4][0])
            is_current_host = currentIP.find(ip) >= 0

            for i in range(0, 4):
                date_format = (now + datetime.timedelta(days=-i)).strftime("%Y-%m-%d")
                desc_log = baseDir + "/postPv." + ip + "_" + date_format + ".log"
                src_log = ""
                if i == 0:
                    src_log = "/data/log/jiemo-api/postPV/postPV.log"
                else:
                    src_log = "/data/log/jiemo-api/postPV/postPV." + date_format
                    if os.path.exists(desc_log):
                        print "exists path", desc_log, "skip"
                        continue

                if is_current_host:
                    cmd = "cp " + src_log + "  " + desc_log
                else:

                    cmd = 'scp root@' + ip + ":" + src_log + "  " + desc_log

                print cmd
                print os.popen(cmd).read()
    if args_lg != 2:
        print args_lg, "params err must use : xxx.py  postPVLogPath  postCountLog"
    score_result = readPVLog(baseDir, sys.argv[1])
    # resultJson = {}
    # resultJson["time"] = long(time.time() * 1000)
    # resultJson["list"] = score_result
    # print JSONEncoder().encode(resultJson)
    print "cost time", datetime.datetime.now() - s

    exit(0)
