# -*- coding: utf8
import logging
import os
import socket
import sys

import datetime

from JiemoCodis import JimeoCodis
from Jiemo_logger import Logger
from JiemoConfig import Config

reload(sys)
# 2017/3/23 10:15
__author__ = 'haizhu'

import math
import time

logger = logging.getLogger()

loggerMarkdown = logging.getLogger("markdown")
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
# specialFriend(12, AppVer.VER_1_3_30, "特别好友"), // 特别好友
# recommendTopic(13, AppVer.VER_1_3_90, "分发话题"), // 分发话题
# link(14, AppVer.VER_1_3_90, "链接"), //

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
                   10: 6.,
                   11: 1.8,
                   12: 0,
                   13: 0,
                   14: 0,
                   15: 1,
                   16: 0,
                   17: 0,
                   18: 0,
                   19: 0,
                   20: 0
                   }

# 每个操作对应的基础值
POST_FORWORD_BASE_SCORE = 3.0;
POST_COMMENT_BASE_SCORE = 2.0
POST_FAV_BASE_SCORE = 1.0

# 是否打印中间信息
PRINT_INFO = False

MAX_DAYS = 2;
# 时间降序因子 【0，3]天，换算成分钟[0,3*24*60]
MAX_MINU = MAX_DAYS * 24 * 60.

MIN_SCORE = 20;

MIN_PV_COUNT = 100

lockfile = "/data/postPV/lock"


# pv影响影响因子 例如pv越大数值越可靠 范围[50,100]
def pvCountFactor(currentPVCount, maxPVCount):
    # print currentPVCount, maxPVCount
    # y = (1 + sin(π * ((x - 2500) / 5000)))
    # return 100 * ((1 + math.sin(math.pi * ((currentPVCount * 1.) / maxPVCount - 0.5))) / 2)
    # 范围[30，100]
    return 90 * ((1 + math.sin(math.pi * ((currentPVCount * 1.) / maxPVCount - 0.5))) / 2) + 10

    pass


def timeDescFactor(currentTime):
    # (cos(x * π / 168) + 1) / 2
    if MAX_MINU <= currentTime:
        return 0
    return math.pow(100 * ((math.cos(currentTime * math.pi / MAX_MINU) + 1) / 2), 2)
    pass


def getMapValue(collections, k):
    if collections.has_key(k):
        return collections[k];
    return 0;
    pass


def readPVLog(log_paths, postCountLog):
    print "开始计算权值", postCountLog

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
    logger.info("权值求和计算完成，共计%d记录满足要求", len(post_score))
    # 权值求和计算完成

    # 求每个用户的权值和
    pv_counts = {};
    post_types = {}
    hotRecommendPV = {}

    max_pv_count = 1;
    for postPVLog in log_paths:
        if postPVLog.startswith(".") or not os.path.exists(os.path.join(baseDir, postPVLog)):
            logger.info("skip file %s", f.name)
            continue
        f = open(os.path.join(baseDir, postPVLog))
        logger.info("read file %s", f.name)

        line = f.readline().strip()
        while line:
            bases = line.split("|")
            line = f.readline().strip()
            if len(bases) >= 2:
                datas = bases[1].split(" ")
                postId = (datas[0])
                if post_score.has_key(postId):

                    dlg = len(datas)
                    if dlg >= 3:
                        if hotRecommendPV.has_key(postId):
                            hotRecommendPV[postId] += 1;
                        else:
                            hotRecommendPV[postId] = 1;

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

    logger.info("max_pv_count %d", max_pv_count)
    count = 0;
    if PRINT_INFO:
        loggerMarkdown.info("|PV排名|postId|PV|")
        loggerMarkdown.info("|-|-|-|")
        for k, v in sorted(pv_counts.items(), lambda x, y: cmp(int(x[1]), int(y[1])), reverse=True):
            if count > 200:
                break
            count += 1;
            loggerMarkdown.info("%s%d%s%s%s%d%s", "|", count, "|",
                                "[" + k + "](/post/search/byIDorUUID?postId=" + k + ")", "|", v, "|")

    # 开始求权值排名
    score_result = {}
    if PRINT_INFO:
        loggerMarkdown.info("\n|权值求和|postId|score|")
        loggerMarkdown.info("|-|-|-|")
        count = 0;

    for k, v in sorted(post_score.items(), lambda x, y: cmp(int(x[1]), int(y[1])), reverse=True):
        if v >= MIN_SCORE and pv_counts.has_key(k):
            pvc = pv_counts[k]
            if pvc < MIN_PV_COUNT:
                continue

            if forword_post_scores.has_key(k):  # 如果有转发的权值  也加到源post里面
                v += forword_post_scores[k]
            sv = timeDescFactor(post_create_times[k]) * pvCountFactor(currentPVCount=pvc,
                                                                      maxPVCount=max_pv_count) * v / pvc
            if sv <= 0:
                continue
            bs = POST_TYPE_SCORE[post_types[k]];
            if bs <= 0:
                continue;
            score_result[k] = sv * POST_TYPE_SCORE[post_types[k]]
            if PRINT_INFO:
                count += 1
                loggerMarkdown.info("%s%d%s%s%s%d%s", "|", count, "|", k, "|", v, "|")

    if PRINT_INFO:
        count = 0;
        loggerMarkdown.info("\n|计算后权值排名|postId|score|totalPVCount|recommdPV|totalScore|pvRate|timeDesRate|postType|")
        loggerMarkdown.info("|-|-|-|-|-|-|-|-|-|")
        for k, v in sorted(score_result.items(), lambda x, y: cmp(float(x[1]), float(y[1])), reverse=True):
            count += 1
            # if post_types[k] != 10:
            #     continue
            loggerMarkdown.info("%s %d %s %s %s %f %s %d %s %d %s %d %s %f %s %f %s %s %s",
                                "|", count, "|", "[" + k + "](/post/search/byIDorUUID?postId=" + k + ")", "|", v, "|", \
                                pv_counts[k], "|", getMapValue(hotRecommendPV, k), "|", post_score[k], "|", \
                                pvCountFactor(currentPVCount=pv_counts[k], maxPVCount=max_pv_count), "|", \
                                timeDescFactor(post_create_times[k]), "|", post_types[k], "|")
            # if count > 500:
            #     break
    return score_result
    pass


def initPVLog(baseDir):
    host = "cluster.d.jiemoapp.com"

    if not Config().isProductionEnvironment():
        host = "10.10.5.222"
    cmd = "ping -c 1 {0}".format(host);
    logger.info(os.popen(cmd).read())
    # os.system("rm -rf " + baseDir)
    if not os.path.exists(baseDir):
        os.makedirs(baseDir)

    currentIP = "10.44.201.101"

    log_paths = [];
    for info in socket.getaddrinfo(host, 80, socket.AF_UNSPEC,
                                   socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
        ip = str(info[4][0])
        is_current_host = currentIP.find(ip) >= 0

        for i in range(0, MAX_DAYS + 1):
            date_format = (start_time + datetime.timedelta(days=-i)).strftime("%Y-%m-%d")
            desc_log = baseDir + "/postPv." + ip + "_" + date_format + ".log"
            log_paths.append(desc_log)
            src_log = ""
            if i == 0:
                src_log = "/data/log/jiemo-api/postPV/postPV.log"
            else:
                src_log = "/data/log/jiemo-api/postPV/postPV." + date_format
                if i > 1 and os.path.exists(desc_log):
                    print "exists path", desc_log, "skip"
                    continue

            if is_current_host:
                cmd = "cp " + src_log + "  " + desc_log
            else:

                cmd = 'scp root@' + ip + ":" + src_log + "  " + desc_log

            logger.info(cmd)
            logger.info(os.popen(cmd).read())

    for f in os.listdir(baseDir):
        f = os.path.join(baseDir, f);
        print f
        if f in log_paths:
            continue
        else:
            os.remove(f)
        pass
    return log_paths
    pass


def initPostList(baseDir):
    result_path = os.path.join(baseDir, "postList.log")
    cmd = "/root/shell/runEx.sh /data/java/jiemo-runner \"com.jiemo.runner.stats.PostScorePVAnalysisRunner {0}  {1} \"".format(
        MAX_DAYS * 24, result_path)
    logger.info(cmd)

    logger.info(os.popen(cmd).read())
    logger.info("get post list path=%s", result_path)
    return result_path
    pass


def unLock():
    pass


if __name__ == '__main__':

    last_failure = False
    # lock
    try:
        fd = os.open(lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        os.close(fd)
    except OSError as e:
        print os.popen("sh /root/monitor/send_sms.sh '热门异常，请检查grape /opt/postPV/postPV.py' 18611522617").read()
        print "获取锁失败", e
        os.remove(lockfile)
        last_failure = True
        # exit(-1)

    Logger();

    start_time = datetime.datetime.now()
    PRINT_INFO = len(sys.argv) > 1;
    if not Config().isProductionEnvironment():
        MIN_SCORE = 1
        MIN_PV_COUNT = 1;
        pass

    baseDir = "/data/postPV"

    score_result = readPVLog(initPVLog(baseDir), initPostList(baseDir))

    if len(score_result) < 1:
        print "没有结果"
        logger.info("没有结果")
        exit(0)

    codis = JimeoCodis().getCodis();
    # 存储处理
    key = "z.hplt"
    codis.delete(key)
    logger.info("before %s", codis.zrangebyscore(key, "-inf", "+inf"));
    codis.zadd(key, **score_result)
    logger.info("after %s", codis.zrangebyscore(key, "-inf", "+inf"));

    cost_time = datetime.datetime.now() - start_time
    desc = "共计{0}条数据   上次更新时间->{1}   更新耗时—>{2}".format(str(len(score_result)), str(datetime.datetime.now()), str(
        cost_time))
    codis.set("z.hplDesc", desc)

    codis.close()
    print "cost time", cost_time
    logger.info("cost time %s", cost_time)

    # 解锁
    os.close(fd)

    if last_failure:
        print os.popen("sh /root/monitor/send_sms.sh 'postPV已经自动恢复，不用干预' 18611522617").read()

    exit(0)
