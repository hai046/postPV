# -*- coding: utf8
import os
import socket
import sys

reload(sys)
sys.setdefaultencoding("utf-8")
# 2017/3/23 10:15
__author__ = 'haizhu'

# import socket
import datetime

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
POST_TYPE_SCORE = {1: 1.,
                   2: 1.2,
                   3: 1,
                   4: 0,
                   5: 0,
                   6: 0,
                   7: 0,
                   8: 2.2,
                   9: 1.6,
                   10: 3.2,
                   11: 1.8}

POST_FORWORD_BASE_SCORE = 4.0;
POST_COMMENT_BASE_SCORE = 2.0
POST_FAV_BASE_SCORE = 1.0

# # pv影响影响因子 例如pv越大数值越可靠
# def pvFactor(pvCount):
#
#
# pass

PRINT_INFO = False


def readPVLog(baseDir, postCountLog):
    # # 开始计算权值
    f = open(postCountLog)
    line = f.readline()
    postScore = {}
    while line:
        line = line.strip()
        bases = line.split(" ")
        line = f.readline().strip()
        if len(bases) == 5:
            postId = (bases[0])
            forwordCount = int(bases[1])
            favCount = int(bases[2])
            commendCount = int(bases[3])
            commendUserCount = int(bases[4])

            # if "2635773" == postId:
            #     print bases
            score = forwordCount * POST_FORWORD_BASE_SCORE \
                    + favCount * POST_FAV_BASE_SCORE \
                    + (commendUserCount + (
                commendCount - commendUserCount) / 10) * POST_COMMENT_BASE_SCORE  # 相同的人评论10条算一个
            if score <= 0:
                continue

            if postScore.has_key(postId):
                postScore[postId] += score
            else:
                postScore[postId] = score
    f.close()
    print "权值求和计算完成，共计", len(postScore), "条记录满足要求"
    # 权值求和计算完成

    # 求每个用户的权值和
    pv_counts = {};
    post_types = {}
    start_time = datetime.datetime.now()
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
                # date = bases[0]
                # t = start_time - datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
                datas = bases[1].split(" ")
                postId = (datas[0])
                # print postId, postType
                if postScore.has_key(postId):
                    postType = int(datas[1])
                    post_types[postId] = postType
                    if pv_counts.has_key(postId):
                        pv_counts[postId] += 1;
                    else:
                        pv_counts[postId] = 1

        f.close()

    count = 0;
    if PRINT_INFO:
        print "|PV排名|postId|PV|"
        print "|-|-|-|"
        for k, v in sorted(pv_counts.items(), lambda x, y: cmp(x[1], y[1]), reverse=True):
            if count > 200:
                break
            # if post_types[k] != 10:
            #     continue
            count += 1;
            print "|", count, "|", "https://sol.jiemosrc.com/post/search/byIDorUUID?postId=" + k, "|", v, "|"

    # 开始求权值排名
    score_result = {}
    if PRINT_INFO:
        print "\n|权值求和|postId|score|"
        print "|-|-|-|"
        count = 0;
    for k, v in sorted(postScore.items(), lambda x, y: cmp(x[1], y[1]), reverse=True):
        if v >= 20.0 and pv_counts.has_key(k):
            pvc = pv_counts[k]
            if pvc < 100:
                continue
            if PRINT_INFO:
                count += 1
                print "|", count, "|", k, "|", v, "|"
            if score_result.has_key(k):
                score_result[k] += v / (pvc / 1000.0)
            else:
                score_result[k] = v / (pvc / 1000.0)

    return sorted(score_result.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)


if __name__ == '__main__':
    args_lg = len(sys.argv)

    baseDir = "/Users/haizhu/Downloads/result/postPV";
    now = datetime.datetime.now()
    host = "search.d.jiemoapp.com"
    # host = "cluster.d.jiemoapp.com"

    baseDir = "/data/postPV"

    if not os.path.exists(baseDir):
        os.makedirs(baseDir)

    currentIP = os.popen("ifconfig").read()
    # print currentIP
    hasFile = True
    postPVFiles = []

    for info in socket.getaddrinfo(host, 80, socket.AF_UNSPEC,
                                   socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
        ip = str(info[4][0])
        for i in range(0, 7):
            date_format = (now + datetime.timedelta(days=-i)).strftime("%Y-%m-%d")
            postPVFile = ""
            desc_log = baseDir + "/postPv." + ip + "_" + date_format + ".log"
            src_log = ""
            if i == 0:
                src_log = "/data/log/jiemo-api/postPV/postPV.log"
            else:
                src_log = "/data/log/jiemo-api/postPV/postPV." + date_format + ".log"

            print src_log
            if hasFile:
                if os.path.exists(postPVFile):
                    postPVFiles.append(postPVFile)
            else:
                if os.path.exists(postPVFile):
                    os.remove(postPVFile)
                cmd = 'scp root@' + ip + ":/data/log/jiemo-api/postPV/postPV.log  " + postPVFile
                output = os.popen(cmd)
                print cmd
                print output.read().strip()
                postPVFiles.append(postPVFile)
    print postPVFiles
    # exit(0)
    # / data / log / postCounts_03 - 23_15.log
    if args_lg != 2:
        print args_lg, "params err must use : xxx.py  postPVLogPath  postCountLog"

    start_time = now + datetime.timedelta(days=-6)

    print start_time.strftime("%Y-%m-%d")
    print now
    print start_time

    score_result = readPVLog(baseDir, sys.argv[1])
    if PRINT_INFO:
        count = 0;
        print "\n|计算后权值排名|postId|score|"
        print "|-|-|-|"
        for k, v in score_result:
            count += 1
            print "|", count, "|", "https://sol.jiemosrc.com/post/search/byIDorUUID?postId=" + k, "|", v, "|"
            if count > 200:
                break
