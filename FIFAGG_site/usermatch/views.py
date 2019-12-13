from django.shortcuts import render
import requests
from usermatch.models import Match
from django.utils import timezone

# 피파 매치 정보 검색
def home_view(request):
    return render(request, 'usermatch/home.html')

def recentmatch_summary(request):

    if request.method == "GET":
        get_nickname = request.GET.get('search_nickname')

        user_exist = False
        api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50X2lkIjoiMTI3NTA5OTk2MyIsImF1dGhfaWQiOiIyIiwidG9rZW5fdHlwZSI6IkFjY2Vzc1Rva2VuIiwic2VydmljZV9pZCI6IjQzMDAxMTQ4MSIsIlgtQXBwLVJhdGUtTGltaXQiOiIyMDAwMDoxMCIsIm5iZiI6MTU3MjI2NjAzNywiZXhwIjoxNjM1MzM4MDM3LCJpYXQiOjE1NzIyNjYwMzd9.LBndJ2IQUk4HmWpEVM4iDuOYxv767S0pfxujaZFlgGI'

        userinfo = {}
        recentmatches = {} # 안 쓰는 듯
        matchdetail = []
        matchid_list = []

        userinfo_url = 'https://api.nexon.co.kr/fifaonline4/v1.0/users?nickname=' + str(get_nickname)
        header = {"Authorization":api_key}
        userinfo_response = requests.get(userinfo_url, headers = header)

        if(userinfo_response.status_code == 200):
            #### 유저 정보 ####
            user_exist = True
            userinfo_data = userinfo_response.json()
            userinfo['accessId'] = userinfo_data["accessId"]
            userinfo['nickname'] = userinfo_data["nickname"]
            userinfo['level'] = userinfo_data["level"]

            matchtype_url = "https://static.api.nexon.co.kr/fifaonline4/latest/matchtype.json"
            matchtype_res = requests.get(matchtype_url, headers = header)

            if(matchtype_res.status_code == 200):
                matchtype_data = matchtype_res.json()
            else:
                print("Error Code:" + matchtype_res.status_code)

            matchNum = 25
            #### 최근 20경기 매치id ####
            recentmatches_params = {"accessId":userinfo_data["accessId"], 'matchtype':matchtype_data[0]['matchtype'], 'offset':0, 'limit':matchNum}
            recentmatches_url = 'https://api.nexon.co.kr/fifaonline4/v1.0/users/{accessid}/matches?matchtype={matchtype}&offset={offset}&limit={limit}'.format(accessid=recentmatches_params["accessId"], matchtype=recentmatches_params['matchtype'], offset=recentmatches_params['offset'], limit=recentmatches_params['limit'] )
            recentmatches_res = requests.get(recentmatches_url, headers=header)

            if(recentmatches_res.status_code==200):
                recentmatches_data = recentmatches_res.json()
            else:
                print("Error Code:" + recentmatches_res.status_code)

            for matchid in recentmatches_data:

                matchid_list.append(matchid)
                matchdetail_url = 'https://api.nexon.co.kr/fifaonline4/v1.0/matches/{matchid}'.format(matchid=matchid)
                matchdetail_res = requests.get(matchdetail_url, headers=header)
                if(matchdetail_res.status_code==200):
                    matchdetail_data = matchdetail_res.json()
                    matchdetail.append(matchdetail_data)
                else:
                    print("Error Code:" + matchdetail_res.status_code)

            #### 최근 20경기 통계 기록 ####
            recentmatchInfo = []
            recentsummary = {}
            recent_winlose = []
            recent_score = []
            recent_against_score = []
            goal_count = []
            shoot_count = []
            possession = []
            pass_try = []
            pass_success = []
            dribble = []

            for matchid,detail in zip(matchid_list, matchdetail):
                if len(detail['matchInfo']) == 2:
                    if detail['matchInfo'][0]['nickname'] == str(get_nickname):
                        search_info = detail['matchInfo'][0]
                        opponent_info = detail['matchInfo'][1]
                    else:
                        search_info = detail['matchInfo'][1]
                        opponent_info = detail['matchInfo'][0]
                else:
                    search_info = detail['matchInfo'][0]
                    opponent_info = None

                if search_info['matchDetail']['matchEndType'] == 0:
                    recent_winlose.append(search_info['matchDetail']['matchResult'])

                elif search_info['matchDetail']['matchEndType'] == 1:
                    recent_winlose.append('몰수승')
                else:
                    recent_winlose.append('몰수패')

                recentmatchInfo.append({
                    'winlose': recent_winlose[-1],
                    'myscore': search_info['shoot']['goalTotal'],
                    'opponentscore': (0 if opponent_info is None else opponent_info['shoot']['goalTotal']) + search_info['shoot']['ownGoal'],
                    'myteam': search_info['nickname'],
                    'opponentteam': opponent_info['nickname'],
                    'matchdate': detail['matchDate']
                })

                # DB 적재
                # m = Match(matchid=matchid, result=recent_winlose[-1], tddate=detail['matchDate'])
                # m.save()

                recent_score.append(search_info['shoot']['goalTotal'])
                recent_against_score.append((0 if opponent_info is None else opponent_info['shoot']['goalTotal']) + search_info['shoot']['ownGoal'])
                goal_count.append(search_info['shoot']['goalTotal'])
                shoot_count.append(search_info['shoot']['shootTotal'])
                possession.append(search_info['matchDetail']['possession'])
                pass_try.append(search_info['pass']['passTry'])
                pass_success.append(search_info['pass']['passSuccess'])
                dribble.append(search_info['matchDetail']['dribble'])

            recentsummary['win'] = '0' if (len(recent_winlose) == 0) else recent_winlose.count('승') + recent_winlose.count('몰수승')
            recentsummary['lose'] = '0' if (len(recent_winlose) == 0) else recent_winlose.count('패') + recent_winlose.count('몰수패')
            recentsummary['draw'] = '0' if (len(recent_winlose) == 0) else recent_winlose.count('무')
            recentsummary['avg_winrate'] = '경기기록없음' if (len(recent_winlose) == 0) else str(round(((recent_winlose.count('승') + recent_winlose.count('몰수승')) / len(recent_winlose))*100,1)) + "%"
            recentsummary['avg_score'] = '득점기록없음' if (len(recent_score) == 0) else round((sum(recent_score) / len(recent_score)),1)
            recentsummary['avg_against_score'] = '실점기록없음' if (len(recent_against_score) == 0) else round((sum(recent_against_score) / len(recent_against_score)),1)
            recentsummary['goal_successrate'] = '슈팅기록없음' if (sum(shoot_count) == 0) else str(round((sum(goal_count) / sum(shoot_count))*100,1)) + "%"
            recentsummary['pass_successrate'] = '패스기록없음' if (sum(pass_try) == 0) else f"{sum(pass_success)} / {sum(pass_try)} ({str(round((sum(pass_success) / sum(pass_try))*100,1)) + '%'})"
            recentsummary['avg_dribble'] = '드리블기록없음' if (len(dribble) == 0) else str(round((sum(dribble) / len(dribble)),1)) + "m"

        else:
            print("Error Code:" + userinfo_response.status_code)

    return render (request, 'usermatch/match/recentmatch_summary.html', {'user_exist': user_exist, 'userinfo': userinfo, 'recentsummary': recentsummary, 'matchNum': matchNum, 'recentmatchInfo': recentmatchInfo})


def match_detail(request):

    if request.method == "GET":
        get_nickname = request.GET.get('search_nickname')

        user_exist = False
        api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50X2lkIjoiMTI3NTA5OTk2MyIsImF1dGhfaWQiOiIyIiwidG9rZW5fdHlwZSI6IkFjY2Vzc1Rva2VuIiwic2VydmljZV9pZCI6IjQzMDAxMTQ4MSIsIlgtQXBwLVJhdGUtTGltaXQiOiIyMDAwMDoxMCIsIm5iZiI6MTU3MjI2NjAzNywiZXhwIjoxNjM1MzM4MDM3LCJpYXQiOjE1NzIyNjYwMzd9.LBndJ2IQUk4HmWpEVM4iDuOYxv767S0pfxujaZFlgGI'

        userinfo = {}
        recentmatches = {} # 안 쓰는 듯
        matchdetail = []
        matchid_list = []

        userinfo_url = 'https://api.nexon.co.kr/fifaonline4/v1.0/users?nickname=' + str(get_nickname)
        header = {"Authorization":api_key}
        userinfo_response = requests.get(userinfo_url, headers = header)

        if(userinfo_response.status_code == 200):
            #### 유저 정보 ####
            user_exist = True
            userinfo_data = userinfo_response.json()
            userinfo['accessId'] = userinfo_data["accessId"]
            userinfo['nickname'] = userinfo_data["nickname"]
            userinfo['level'] = userinfo_data["level"]

            matchtype_url = "https://static.api.nexon.co.kr/fifaonline4/latest/matchtype.json"
            matchtype_res = requests.get(matchtype_url, headers = header)

            if(matchtype_res.status_code == 200):
                matchtype_data = matchtype_res.json()
            else:
                print("Error Code:" + matchtype_res.status_code)

            matchNum = 25
            #### 최근 N경기 매치id ####
            recentmatches_params = {"accessId":userinfo_data["accessId"], 'matchtype':matchtype_data[0]['matchtype'], 'offset':0, 'limit':matchNum}
            recentmatches_url = 'https://api.nexon.co.kr/fifaonline4/v1.0/users/{accessid}/matches?matchtype={matchtype}&offset={offset}&limit={limit}'.format(accessid=recentmatches_params["accessId"], matchtype=recentmatches_params['matchtype'], offset=recentmatches_params['offset'], limit=recentmatches_params['limit'] )
            recentmatches_res = requests.get(recentmatches_url, headers=header)

            if(recentmatches_res.status_code==200):
                recentmatches_data = recentmatches_res.json()
            else:
                print("Error Code:" + recentmatches_res.status_code)

            for matchid in recentmatches_data:

                matchid_list.append(matchid)
                matchdetail_url = 'https://api.nexon.co.kr/fifaonline4/v1.0/matches/{matchid}'.format(matchid=matchid)
                matchdetail_res = requests.get(matchdetail_url, headers=header)
                if(matchdetail_res.status_code==200):
                    matchdetail_data = matchdetail_res.json()
                    matchdetail.append(matchdetail_data)
                else:
                    print("Error Code:" + matchdetail_res.status_code)

            #### 최근 N경기 기록 ####

            recentmatchInfo = []
            # recent_score = []
            # recent_against_score = []
            # goal_count = []
            # shoot_count = []
            # possession = []
            # pass_try = []
            # pass_success = []
            # dribble = []

            for matchid,detail in zip(matchid_list, matchdetail):
                if len(detail['matchInfo']) == 2:
                    if detail['matchInfo'][0]['nickname'] == str(get_nickname):
                        search_info = detail['matchInfo'][0]
                        opponent_info = detail['matchInfo'][1]
                    else:
                        search_info = detail['matchInfo'][1]
                        opponent_info = detail['matchInfo'][0]
                else:
                    search_info = detail['matchInfo'][0]
                    opponent_info = None

                recent_winlose = ""
                if search_info['matchDetail']['matchEndType'] == 0:
                    recent_winlose = search_info['matchDetail']['matchResult']

                elif search_info['matchDetail']['matchEndType'] == 1:
                    recent_winlose = '몰수승'
                else:
                    recent_winlose = '몰수패'

                # DB 적재
                # m = Match(matchid=matchid, result=recent_winlose[-1], tddate=detail['matchDate'])
                # m.save()

                # matchdate.append(detail['matchDate'])
                # recent_score.append(search_info['shoot']['goalTotal'])
                # recent_against_score.append((0 if opponent_info is None else opponent_info['shoot']['goalTotal']) + search_info['shoot']['ownGoal'])
                # goal_count.append(search_info['shoot']['goalTotal'])
                # shoot_count.append(search_info['shoot']['shootTotal'])
                # possession.append(search_info['matchDetail']['possession'])
                # pass_try.append(search_info['pass']['passTry'])
                # pass_success.append(search_info['pass']['passSuccess'])
                # dribble.append(search_info['matchDetail']['dribble'])
                recentmatchInfo.append({
                    'winlose': recent_winlose,
                    'myscore': search_info['shoot']['goalTotal'],
                    'opponentscore': (0 if opponent_info is None else opponent_info['shoot']['goalTotal']) + search_info['shoot']['ownGoal'],
                    'myteam': search_info['nickname'],
                    'opponentteam': opponent_info['nickname'],
                    'matchdate': detail['matchDate']
                })

            # recentmatchInfo['winlose'] = recent_winlose
            # recentmatchInfo['myscore'] = recent_score
            # recentmatchInfo['opponentscore'] = recent_against_score
            # recentmatchInfo['myteam'] = search_info['nickname']
            # recentmatchInfo['opponentteam'] = opponent_info['nickname']
            # recentmatchInfo['matchdate'] = matchdate

        else:
            print("Error Code:" + userinfo_response.status_code)

    return render (request, 'usermatch/match/match_detail.html', {'user_exist': user_exist, 'userinfo': userinfo, 'recentmatchInfo': recentmatchInfo, 'matchNum': matchNum})
