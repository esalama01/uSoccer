from curl_cffi import requests
from bs4 import BeautifulSoup
import json
import re
import json5
import tempfile
import pandas as pd
from socceraction.data.opta.parsers import WhoScoredParser
from socceraction.spadl.opta import convert_to_actions
from socceraction.data.opta.loader import _eventtypesdf
from socceraction.spadl import config as spadlconfig
import socceraction.vaep.features as fs
import socceraction.vaep.labels as lab
#import time

all_regions_raw = r"""
[{type:1, id:248, flg:'flg-caf', name: 'Africa', tournaments: [{id:290, url:'/regions/248/tournaments/290/africa-caf-champions-league', name:'CAF Champions League', sortOrder:12},{id:754, url:'/regions/248/tournaments/754/africa-african-nations-championship-qualification', name:'African Nations Championship Qualification', sortOrder:0},{id:762, url:'/regions/248/tournaments/762/africa-caf-champions-league-qualification', name:'CAF Champions League Qualification', sortOrder:0},{id:574, url:'/regions/248/tournaments/574/africa-caf-confederations-cup', name:'CAF Confederations Cup', sortOrder:0},{id:747, url:'/regions/248/tournaments/747/africa-africa-cup-of-nations-qualification', name:'Africa Cup of Nations Qualification', sortOrder:10},{id:573, url:'/regions/248/tournaments/573/africa-caf-super-cup', name:'CAF Super Cup', sortOrder:11},{id:505, url:'/regions/248/tournaments/505/africa-cecafa-senior-challenge-cup', name:'CECAFA Senior Challenge Cup', sortOrder:0}]},
{type:0, id:3, flg:'flg-al', name: 'Albania', tournaments: [{id:182, url:'/regions/3/tournaments/182/albania-kategoria-superiore', name:'Kategoria Superiore', sortOrder:0},{id:451, url:'/regions/3/tournaments/451/albania-kategoria-superiore-qualification', name:'Kategoria Superiore qualification', sortOrder:0},{id:618, url:'/regions/3/tournaments/618/albania-kupa-e-shqipërisë', name:'Kupa e Shqipërisë', sortOrder:0}]},
{type:0, id:4, flg:'flg-dz', name: 'Algeria', tournaments: [{id:281, url:'/regions/4/tournaments/281/algeria-ligue-professionnelle-1', name:'Ligue Professionnelle 1', sortOrder:0}]},
{type:0, id:6, flg:'flg-ad', name: 'Andorra', tournaments: [{id:619, url:'/regions/6/tournaments/619/andorra-andorran-cup', name:'Andorran Cup', sortOrder:0},{id:142, url:'/regions/6/tournaments/142/andorra-primera-divisio', name:'Primera Divisio', sortOrder:0},{id:526, url:'/regions/6/tournaments/526/andorra-primera-divisio-qualification', name:'Primera Divisio Qualification', sortOrder:0}]},
{type:0, id:11, flg:'flg-ar', name: 'Argentina', tournaments: [{id:68, url:'/regions/11/tournaments/68/argentina-liga-profesional', name:'Liga Profesional', sortOrder:10},{id:317, url:'/regions/11/tournaments/317/argentina-primera-b-nacional', name:'Primera B Nacional', sortOrder:0},{id:697, url:'/regions/11/tournaments/697/argentina-copa-de-la-superliga', name:'Copa de la Superliga', sortOrder:10},{id:504, url:'/regions/11/tournaments/504/argentina-cup', name:'Cup', sortOrder:10},{id:541, url:'/regions/11/tournaments/541/argentina-super-cup', name:'Super Cup', sortOrder:10},{id:605, url:'/regions/11/tournaments/605/argentina-argentina-4', name:'Argentina 4', sortOrder:0},{id:463, url:'/regions/11/tournaments/463/argentina-primera-b-metropolitana', name:'Primera B Metropolitana', sortOrder:0}]},
{type:0, id:12, flg:'flg-am', name: 'Armenia', tournaments: [{id:256, url:'/regions/12/tournaments/256/armenia-cup', name:'Cup', sortOrder:0},{id:156, url:'/regions/12/tournaments/156/armenia-premier-league', name:'Premier League', sortOrder:0},{id:270, url:'/regions/12/tournaments/270/armenia-super-cup', name:'Super Cup', sortOrder:0}]},
{type:1, id:249, flg:'flg-cas', name: 'Asia', tournaments: [{id:287, url:'/regions/249/tournaments/287/asia-afc-champions-league', name:'AFC Champions League', sortOrder:10},{id:212, url:'/regions/249/tournaments/212/asia-east-asian-championship', name:'East Asian Championship', sortOrder:12},{id:241, url:'/regions/249/tournaments/241/asia-gulf-cup', name:'Gulf Cup', sortOrder:13},{id:763, url:'/regions/249/tournaments/763/asia-afc-champions-league-elite-qualification', name:'AFC Champions League Elite Qualification', sortOrder:0},{id:644, url:'/regions/249/tournaments/644/asia-afc-u23-asian-cup', name:'AFC U23 Asian Cup', sortOrder:0},{id:753, url:'/regions/249/tournaments/753/asia-asean-championship-qualification', name:'ASEAN Championship Qualification', sortOrder:0},{id:748, url:'/regions/249/tournaments/748/asia-asian-cup-qualification', name:'Asian Cup Qualification', sortOrder:0},{id:575, url:'/regions/249/tournaments/575/asia-afc-cup', name:'AFC Cup', sortOrder:9},{id:490, url:'/regions/249/tournaments/490/asia-aff-championship', name:'AFF Championship', sortOrder:11},{id:635, url:'/regions/249/tournaments/635/asia-premier-league-asia-trophy', name:'Premier League Asia Trophy', sortOrder:0}]},
{type:0, id:14, flg:'flg-au', name: 'Australia', tournaments: [{id:194, url:'/regions/14/tournaments/194/australia-a-league', name:'A-League', sortOrder:0},{id:312, url:'/regions/14/tournaments/312/australia-australia-2', name:'Australia 2', sortOrder:0},{id:577, url:'/regions/14/tournaments/577/australia-australia-cup', name:'Australia Cup', sortOrder:0},{id:612, url:'/regions/14/tournaments/612/australia-australia-4', name:'Australia 4', sortOrder:0},{id:567, url:'/regions/14/tournaments/567/australia-npl', name:'NPL', sortOrder:0}]},
{type:0, id:15, flg:'flg-at', name: 'Austria', tournaments: [{id:53, url:'/regions/15/tournaments/53/austria-erste-liga', name:'Erste Liga', sortOrder:0},{id:83, url:'/regions/15/tournaments/83/austria-stiegl-cup', name:'Stiegl Cup', sortOrder:0},{id:32, url:'/regions/15/tournaments/32/austria-bundesliga', name:'Bundesliga', sortOrder:10},{id:441, url:'/regions/15/tournaments/441/austria-regionalliga', name:'Regionalliga', sortOrder:0}]},
{type:0, id:16, flg:'flg-az', name: 'Azerbaijan', tournaments: [{id:173, url:'/regions/16/tournaments/173/azerbaijan-premier-league', name:'Premier League', sortOrder:0},{id:615, url:'/regions/16/tournaments/615/azerbaijan-azerbaijan-cup-1', name:'Azerbaijan Cup 1', sortOrder:0}]},
{type:0, id:18, flg:'flg-bh', name: 'Bahrain', tournaments: [{id:302, url:'/regions/18/tournaments/302/bahrain-1-division', name:'1. Division', sortOrder:0}]},
{type:0, id:21, flg:'flg-by', name: 'Belarus', tournaments: [{id:157, url:'/regions/21/tournaments/157/belarus-premier-league', name:'Premier League', sortOrder:0},{id:657, url:'/regions/21/tournaments/657/belarus-super-cup', name:'Super Cup', sortOrder:0},{id:620, url:'/regions/21/tournaments/620/belarus-belarus-cup-1', name:'Belarus Cup 1', sortOrder:0},{id:480, url:'/regions/21/tournaments/480/belarus-premier-league-qualification', name:'Premier League Qualification', sortOrder:0}]},
{type:0, id:22, flg:'flg-be', name: 'Belgium', tournaments: [{id:28, url:'/regions/22/tournaments/28/belgium-cup', name:'Cup', sortOrder:10},{id:18, url:'/regions/22/tournaments/18/belgium-jupiler-pro-league', name:'Jupiler Pro League', sortOrder:10},{id:117, url:'/regions/22/tournaments/117/belgium-super-cup', name:'Super Cup', sortOrder:10},{id:161, url:'/regions/22/tournaments/161/belgium-play-off', name:'Play Off', sortOrder:0},{id:137, url:'/regions/22/tournaments/137/belgium-second-division', name:'Second Division', sortOrder:0},{id:459, url:'/regions/22/tournaments/459/belgium-3-division', name:'3. Division', sortOrder:0}]},
{type:0, id:27, flg:'flg-bo', name: 'Bolivia', tournaments: [{id:255, url:'/regions/27/tournaments/255/bolivia-liga-de-fútbol-profesional', name:'Liga de Fútbol Profesional', sortOrder:0},{id:528, url:'/regions/27/tournaments/528/bolivia-primera-division-qualification', name:'Primera Division Qualification', sortOrder:0}]},
{type:0, id:28, flg:'flg-ba', name: 'Bosnia-Herzegovina', tournaments: [{id:404, url:'/regions/28/tournaments/404/bosnia-herzegovina-1-division', name:'1. Division', sortOrder:0},{id:616, url:'/regions/28/tournaments/616/bosnia-herzegovina-bosnia-herzegovina-cup-1', name:'Bosnia-Herzegovina Cup 1', sortOrder:0},{id:174, url:'/regions/28/tournaments/174/bosnia-herzegovina-premier-league', name:'Premier League', sortOrder:0}]},
{type:0, id:31, flg:'flg-br', name: 'Brazil', tournaments: [{id:95, url:'/regions/31/tournaments/95/brazil-brasileirão', name:'Brasileirão', sortOrder:90},{id:269, url:'/regions/31/tournaments/269/brazil-serie-b', name:'Serie B', sortOrder:0},{id:321, url:'/regions/31/tournaments/321/brazil-serie-c', name:'Serie C', sortOrder:0},{id:383, url:'/regions/31/tournaments/383/brazil-cup', name:'Cup', sortOrder:10},{id:564, url:'/regions/31/tournaments/564/brazil-cup-nordeste', name:'Cup Nordeste', sortOrder:0},{id:654, url:'/regions/31/tournaments/654/brazil-sao-paulo-youth-cup', name:'Sao Paulo Youth Cup', sortOrder:0},{id:570, url:'/regions/31/tournaments/570/brazil-serie-d', name:'Serie D', sortOrder:0}]},
{type:0, id:34, flg:'flg-bg', name: 'Bulgaria', tournaments: [{id:119, url:'/regions/34/tournaments/119/bulgaria-a-pfg', name:'A PFG', sortOrder:0},{id:398, url:'/regions/34/tournaments/398/bulgaria-b-pfg', name:'B PFG', sortOrder:0},{id:143, url:'/regions/34/tournaments/143/bulgaria-cup', name:'Cup', sortOrder:0},{id:169, url:'/regions/34/tournaments/169/bulgaria-super-cup', name:'Super Cup', sortOrder:0},{id:646, url:'/regions/34/tournaments/646/bulgaria-first-professional-league-qualification', name:'First Professional League Qualification', sortOrder:0}]},
{type:0, id:38, flg:'flg-cm', name: 'Cameroon', tournaments: [{id:247, url:'/regions/38/tournaments/247/cameroon-1-division', name:'1. Division', sortOrder:0}]},
{type:0, id:39, flg:'flg-ca', name: 'Canada', tournaments: [{id:735, url:'/regions/39/tournaments/735/canada-championship', name:'Championship', sortOrder:0},{id:363, url:'/regions/39/tournaments/363/canada-csl', name:'CSL', sortOrder:0}]},
{type:0, id:44, flg:'flg-cl', name: 'Chile', tournaments: [{id:147, url:'/regions/44/tournaments/147/chile-clausura', name:'Clausura', sortOrder:0},{id:395, url:'/regions/44/tournaments/395/chile-cup', name:'Cup', sortOrder:0},{id:554, url:'/regions/44/tournaments/554/chile-super-cup', name:'Super Cup', sortOrder:0}]},
{type:0, id:45, flg:'flg-cn', name: 'China', tournaments: [{id:162, url:'/regions/45/tournaments/162/china-super-league', name:'Super League', sortOrder:10},{id:640, url:'/regions/45/tournaments/640/china-cup', name:'Cup', sortOrder:0},{id:591, url:'/regions/45/tournaments/591/china-super-cup', name:'Super Cup', sortOrder:0}]},
{type:0, id:48, flg:'flg-co', name: 'Colombia', tournaments: [{id:193, url:'/regions/48/tournaments/193/colombia-categoria-primera-a', name:'Categoria Primera A', sortOrder:0},{id:590, url:'/regions/48/tournaments/590/colombia-colombia-cup-1', name:'Colombia Cup 1', sortOrder:0}]},
{type:0, id:53, flg:'flg-cr', name: 'Costa Rica', tournaments: [{id:425, url:'/regions/53/tournaments/425/costa-rica-liga-de-ascenso', name:'Liga de Ascenso', sortOrder:0},{id:238, url:'/regions/53/tournaments/238/costa-rica-primera-division', name:'Primera Division', sortOrder:0}]},
{type:0, id:55, flg:'flg-hr', name: 'Croatia', tournaments: [{id:401, url:'/regions/55/tournaments/401/croatia-2-division', name:'2. Division', sortOrder:0},{id:109, url:'/regions/55/tournaments/109/croatia-cup', name:'Cup', sortOrder:0},{id:82, url:'/regions/55/tournaments/82/croatia-prva-hnl', name:'Prva HNL', sortOrder:10},{id:133, url:'/regions/55/tournaments/133/croatia-super-cup', name:'Super Cup', sortOrder:10}]},
{type:0, id:57, flg:'flg-cy', name: 'Cyprus', tournaments: [{id:402, url:'/regions/57/tournaments/402/cyprus-2-division', name:'2. Division', sortOrder:0},{id:236, url:'/regions/57/tournaments/236/cyprus-cup', name:'Cup', sortOrder:0},{id:185, url:'/regions/57/tournaments/185/cyprus-first-division', name:'First Division', sortOrder:0},{id:283, url:'/regions/57/tournaments/283/cyprus-super-cup', name:'Super Cup', sortOrder:0}]},
{type:0, id:58, flg:'flg-cz', name: 'Czech Republic', tournaments: [{id:84, url:'/regions/58/tournaments/84/czech-republic-cup', name:'Cup', sortOrder:0},{id:234, url:'/regions/58/tournaments/234/czech-republic-druha-league', name:'Druha League', sortOrder:0},{id:78, url:'/regions/58/tournaments/78/czech-republic-gambrinus-league', name:'Gambrinus League', sortOrder:10},{id:455, url:'/regions/58/tournaments/455/czech-republic-super-cup', name:'Super Cup', sortOrder:10}]},
{type:0, id:59, flg:'flg-dk', name: 'Denmark', tournaments: [{id:34, url:'/regions/59/tournaments/34/denmark-1-division', name:'1. Division', sortOrder:0},{id:35, url:'/regions/59/tournaments/35/denmark-2-division', name:'2. Division', sortOrder:0},{id:39, url:'/regions/59/tournaments/39/denmark-cup', name:'Cup', sortOrder:0},{id:1, url:'/regions/59/tournaments/1/denmark-superliga', name:'Superliga', sortOrder:10}]},
{type:0, id:63, flg:'flg-ec', name: 'Ecuador', tournaments: [{id:192, url:'/regions/63/tournaments/192/ecuador-serie-a', name:'Serie A', sortOrder:0}]},
{type:0, id:64, flg:'flg-eg', name: 'Egypt', tournaments: [{id:277, url:'/regions/64/tournaments/277/egypt-premier-league', name:'Premier League', sortOrder:0}]},
{type:0, id:65, flg:'flg-sv', name: 'El Salvador', tournaments: [{id:250, url:'/regions/65/tournaments/250/el-salvador-primera-division', name:'Primera Division', sortOrder:0}]},
{type:0, id:252, flg:'flg-gb-eng', name: 'England', tournaments: [{id:9, url:'/regions/252/tournaments/9/england-league-two', name:'League Two', sortOrder:40},{id:8, url:'/regions/252/tournaments/8/england-league-one', name:'League One', sortOrder:50},{id:7, url:'/regions/252/tournaments/7/england-championship', name:'Championship', sortOrder:130},{id:29, url:'/regions/252/tournaments/29/england-league-cup', name:'League Cup', sortOrder:140},{id:26, url:'/regions/252/tournaments/26/england-fa-cup', name:'FA Cup', sortOrder:150},{id:2, url:'/regions/252/tournaments/2/england-premier-league', name:'Premier League', sortOrder:200},{id:96, url:'/regions/252/tournaments/96/england-community-shield', name:'Community Shield', sortOrder:210},{id:314, url:'/regions/252/tournaments/314/england-national-league', name:'National League', sortOrder:0},{id:389, url:'/regions/252/tournaments/389/england-professional-development-league', name:'Professional Development League', sortOrder:0},{id:315, url:'/regions/252/tournaments/315/england-regional-league', name:'Regional League', sortOrder:0},{id:479, url:'/regions/252/tournaments/479/england-fa-trophy', name:'FA Trophy', sortOrder:10},{id:70, url:'/regions/252/tournaments/70/england-national-league-premier', name:'National League Premier', sortOrder:10},{id:23, url:'/regions/252/tournaments/23/england-papa-john-s-trophy', name:'Papa John\'s Trophy', sortOrder:10},{id:739, url:'/regions/252/tournaments/739/england-women-s-super-league', name:'Women\'s Super League', sortOrder:50}]},
{type:0, id:68, flg:'flg-ee', name: 'Estonia', tournaments: [{id:621, url:'/regions/68/tournaments/621/estonia-cup', name:'Cup', sortOrder:0},{id:405, url:'/regions/68/tournaments/405/estonia-esiliiga', name:'Esiliiga', sortOrder:0},{id:148, url:'/regions/68/tournaments/148/estonia-meistriliiga', name:'Meistriliiga', sortOrder:0},{id:385, url:'/regions/68/tournaments/385/estonia-super-cup', name:'Super Cup', sortOrder:0}]},
{type:1, id:250, flg:'flg-ceu', name: 'Europe', tournaments: [{id:62, url:'/regions/250/tournaments/62/europe-uefa-super-cup', name:'UEFA Super Cup', sortOrder:205},{id:30, url:'/regions/250/tournaments/30/europe-europa-league', name:'Europa League', sortOrder:210},{id:12, url:'/regions/250/tournaments/12/europe-champions-league', name:'Champions League', sortOrder:220},{id:680, url:'/regions/250/tournaments/680/europe-uefa-youth-league', name:'UEFA Youth League', sortOrder:0},{id:760, url:'/regions/250/tournaments/760/europe-conference-league-qualification', name:'Conference League Qualification', sortOrder:10},{id:759, url:'/regions/250/tournaments/759/europe-europa-league-qualification', name:'Europa League Qualification', sortOrder:11},{id:757, url:'/regions/250/tournaments/757/europe-champions-league-qualification', name:'Champions League Qualification', sortOrder:12},{id:741, url:'/regions/250/tournaments/741/europe-women-s-champions-league', name:'Women\'s Champions League', sortOrder:14},{id:715, url:'/regions/250/tournaments/715/europe-conference-league', name:'Conference League', sortOrder:28},{id:751, url:'/regions/250/tournaments/751/europe-european-championship-qualification', name:'European Championship Qualification', sortOrder:209},{id:613, url:'/regions/250/tournaments/613/europe-the-atlantic-cup', name:'The Atlantic Cup', sortOrder:0}]},
{type:0, id:71, flg:'flg-fo', name: 'Faroe Islands', tournaments: [{id:622, url:'/regions/71/tournaments/622/faroe-islands-cup', name:'Cup', sortOrder:0},{id:160, url:'/regions/71/tournaments/160/faroe-islands-formuladeildin', name:'Formuladeildin', sortOrder:0}]},
{type:0, id:73, flg:'flg-fi', name: 'Finland', tournaments: [{id:51, url:'/regions/73/tournaments/51/finland-cup', name:'Cup', sortOrder:0},{id:319, url:'/regions/73/tournaments/319/finland-kakkonen', name:'Kakkonen', sortOrder:0},{id:100, url:'/regions/73/tournaments/100/finland-playoff', name:'Playoff', sortOrder:0},{id:43, url:'/regions/73/tournaments/43/finland-veikkausliiga', name:'Veikkausliiga', sortOrder:0},{id:202, url:'/regions/73/tournaments/202/finland-ykkonen', name:'Ykkonen', sortOrder:0}]},
{type:0, id:74, flg:'flg-fr', name: 'France', tournaments: [{id:54, url:'/regions/74/tournaments/54/france-trophée-des-champions', name:'Trophée des Champions', sortOrder:20},{id:16, url:'/regions/74/tournaments/16/france-coupe-de-france', name:'Coupe de France', sortOrder:24},{id:22, url:'/regions/74/tournaments/22/france-ligue-1', name:'Ligue 1', sortOrder:160},{id:661, url:'/regions/74/tournaments/661/france-ligue-2-qualification', name:'Ligue 2 Qualification', sortOrder:0},{id:320, url:'/regions/74/tournaments/320/france-national', name:'National', sortOrder:0},{id:460, url:'/regions/74/tournaments/460/france-national-2', name:'National 2', sortOrder:0},{id:743, url:'/regions/74/tournaments/743/france-division-1-feminine', name:'Division 1 Feminine', sortOrder:1},{id:660, url:'/regions/74/tournaments/660/france-ligue-1-qualification', name:'Ligue 1 Qualification', sortOrder:10},{id:37, url:'/regions/74/tournaments/37/france-ligue-2', name:'Ligue 2', sortOrder:10}]},
{type:0, id:80, flg:'flg-ge', name: 'Georgia', tournaments: [{id:623, url:'/regions/80/tournaments/623/georgia-cup', name:'Cup', sortOrder:0},{id:168, url:'/regions/80/tournaments/168/georgia-evronuli-liga', name:'Evronuli Liga', sortOrder:0},{id:507, url:'/regions/80/tournaments/507/georgia-evronuli-liga-qualification', name:'Evronuli Liga Qualification', sortOrder:0},{id:522, url:'/regions/80/tournaments/522/georgia-erovnuli-liga-2', name:'Erovnuli Liga 2', sortOrder:0}]},
{type:0, id:81, flg:'flg-de', name: 'Germany', tournaments: [{id:6, url:'/regions/81/tournaments/6/germany-2-bundesliga', name:'2. Bundesliga', sortOrder:10},{id:307, url:'/regions/81/tournaments/307/germany-german-super-cup', name:'German Super Cup', sortOrder:25},{id:3, url:'/regions/81/tournaments/3/germany-bundesliga', name:'Bundesliga', sortOrder:170},{id:673, url:'/regions/81/tournaments/673/germany-2-bundesliga-qualification', name:'2. Bundesliga Qualification', sortOrder:0},{id:308, url:'/regions/81/tournaments/308/germany-3-liga', name:'3. Liga', sortOrder:0},{id:274, url:'/regions/81/tournaments/274/germany-regionalliga', name:'Regionalliga', sortOrder:0},{id:745, url:'/regions/81/tournaments/745/germany-frauen-bundesliga', name:'Frauen-Bundesliga', sortOrder:2},{id:388, url:'/regions/81/tournaments/388/germany-bundesliga-qualification', name:'Bundesliga Qualification', sortOrder:10},{id:24, url:'/regions/81/tournaments/24/germany-dfb-pokal', name:'DFB-Pokal', sortOrder:25}]},
{type:0, id:82, flg:'flg-gh', name: 'Ghana', tournaments: [{id:305, url:'/regions/82/tournaments/305/ghana-premier-league', name:'Premier League', sortOrder:0}]},
{type:0, id:83, flg:'flg-gi', name: 'Gibraltar', tournaments: [{id:633, url:'/regions/83/tournaments/633/gibraltar-gibraltar-cup', name:'Gibraltar Cup', sortOrder:0},{id:632, url:'/regions/83/tournaments/632/gibraltar-gibraltar-premier-league', name:'Gibraltar Premier League', sortOrder:0}]},
{type:0, id:84, flg:'flg-gr', name: 'Greece', tournaments: [{id:69, url:'/regions/84/tournaments/69/greece-cup', name:'Cup', sortOrder:0},{id:65, url:'/regions/84/tournaments/65/greece-super-league', name:'Super League', sortOrder:10},{id:292, url:'/regions/84/tournaments/292/greece-second-division', name:'Second Division', sortOrder:0}]},
{type:0, id:89, flg:'flg-gt', name: 'Guatemala', tournaments: [{id:239, url:'/regions/89/tournaments/239/guatemala-liga-nacional', name:'Liga Nacional', sortOrder:0}]},
{type:0, id:97, flg:'flg-hn', name: 'Honduras', tournaments: [{id:240, url:'/regions/97/tournaments/240/honduras-liga-nacional', name:'Liga Nacional', sortOrder:0}]},
{type:0, id:98, flg:'flg-hk', name: 'Hong Kong', tournaments: [{id:332, url:'/regions/98/tournaments/332/hong-kong-1-division', name:'1. Division', sortOrder:0}]},
{type:0, id:99, flg:'flg-hu', name: 'Hungary', tournaments: [{id:102, url:'/regions/99/tournaments/102/hungary-cup', name:'Cup', sortOrder:0},{id:75, url:'/regions/99/tournaments/75/hungary-nb-i', name:'NB I', sortOrder:0},{id:419, url:'/regions/99/tournaments/419/hungary-nb-ii', name:'NB II', sortOrder:0},{id:132, url:'/regions/99/tournaments/132/hungary-super-cup', name:'Super Cup', sortOrder:0}]},
{type:0, id:100, flg:'flg-is', name: 'Iceland', tournaments: [{id:208, url:'/regions/100/tournaments/208/iceland-1-deild', name:'1. Deild', sortOrder:0},{id:129, url:'/regions/100/tournaments/129/iceland-besta-deildin', name:'Besta Deildin', sortOrder:0},{id:206, url:'/regions/100/tournaments/206/iceland-cup', name:'Cup', sortOrder:0}]},
{type:0, id:101, flg:'flg-in', name: 'India', tournaments: [{id:333, url:'/regions/101/tournaments/333/india-i-league', name:'I League', sortOrder:0},{id:582, url:'/regions/101/tournaments/582/india-indian-super-league', name:'Indian Super League', sortOrder:0}]},
{type:0, id:102, flg:'flg-id', name: 'Indonesia', tournaments: [{id:334, url:'/regions/102/tournaments/334/indonesia-super-liga', name:'Super Liga', sortOrder:0}]},
{type:1, id:247, flg:'flg-cint', name: 'International', tournaments: [{id:656, url:'/regions/247/tournaments/656/international-africa-cup-of-nations-u20', name:'Africa Cup of Nations U20', sortOrder:0},{id:201, url:'/regions/247/tournaments/201/international-euro-u-17', name:'EURO U-17', sortOrder:0},{id:244, url:'/regions/247/tournaments/244/international-friendly-u-21', name:'Friendly U-21', sortOrder:0},{id:219, url:'/regions/247/tournaments/219/international-world-championship-u-17', name:'World Championship U-17', sortOrder:0},{id:89, url:'/regions/247/tournaments/89/international-confederations-cup', name:'Confederations Cup', sortOrder:1},{id:57, url:'/regions/247/tournaments/57/international-club-friendlies', name:'Club Friendlies', sortOrder:11},{id:165, url:'/regions/247/tournaments/165/international-euro-u-19', name:'EURO U-19', sortOrder:15},{id:27, url:'/regions/247/tournaments/27/international-int-friendly', name:'Int. Friendly', sortOrder:15},{id:177, url:'/regions/247/tournaments/177/international-summer-olympics', name:'Summer Olympics', sortOrder:15},{id:203, url:'/regions/247/tournaments/203/international-toulon-tournament', name:'Toulon Tournament', sortOrder:15},{id:144, url:'/regions/247/tournaments/144/international-world-championship-u-20', name:'World Championship U-20', sortOrder:15},{id:67, url:'/regions/247/tournaments/67/international-fifa-club-world-cup', name:'FIFA Club World Cup', sortOrder:29},{id:166, url:'/regions/247/tournaments/166/international-asian-cup', name:'Asian Cup', sortOrder:30},{id:123, url:'/regions/247/tournaments/123/international-euro-u-21', name:'EURO U-21', sortOrder:30},{id:718, url:'/regions/247/tournaments/718/international-world-cup-qualification-afc', name:'World Cup Qualification AFC', sortOrder:31},{id:717, url:'/regions/247/tournaments/717/international-world-cup-qualification-concacaf', name:'World Cup Qualification CONCACAF', sortOrder:32},{id:716, url:'/regions/247/tournaments/716/international-world-cup-qualification-caf', name:'World Cup Qualification CAF', sortOrder:33},{id:719, url:'/regions/247/tournaments/719/international-world-cup-qualification-conmebol', name:'World Cup Qualification CONMEBOL', sortOrder:34},{id:721, url:'/regions/247/tournaments/721/international-world-cup-qualification-uefa', name:'World Cup Qualification UEFA', sortOrder:35},{id:104, url:'/regions/247/tournaments/104/international-africa-cup-of-nations', name:'Africa Cup of Nations', sortOrder:159},{id:36, url:'/regions/247/tournaments/36/international-fifa-world-cup', name:'FIFA World Cup', sortOrder:220},{id:94, url:'/regions/247/tournaments/94/international-copa-america', name:'Copa America', sortOrder:221},{id:124, url:'/regions/247/tournaments/124/international-european-championship', name:'European Championship', sortOrder:250},{id:736, url:'/regions/247/tournaments/736/international-euro-u21-qualification', name:'EURO U21 Qualification', sortOrder:0},{id:690, url:'/regions/247/tournaments/690/international-ofc-u19-championship', name:'OFC U19 Championship', sortOrder:0},{id:563, url:'/regions/247/tournaments/563/international-african-nations-championship', name:'African Nations Championship', sortOrder:15},{id:689, url:'/regions/247/tournaments/689/international-concacaf-nations-league', name:'CONCACAF Nations League', sortOrder:15},{id:769, url:'/regions/247/tournaments/769/international-uefa-nations-league-b-qualification', name:'UEFA Nations League B Qualification', sortOrder:27},{id:768, url:'/regions/247/tournaments/768/international-uefa-nations-league-a-qualification', name:'UEFA Nations League A Qualification', sortOrder:28},{id:686, url:'/regions/247/tournaments/686/international-uefa-nations-league-d', name:'UEFA Nations League D', sortOrder:37},{id:685, url:'/regions/247/tournaments/685/international-uefa-nations-league-c', name:'UEFA Nations League C', sortOrder:38},{id:684, url:'/regions/247/tournaments/684/international-uefa-nations-league-b', name:'UEFA Nations League B', sortOrder:39},{id:683, url:'/regions/247/tournaments/683/international-uefa-nations-league-a', name:'UEFA Nations League A', sortOrder:40},{id:738, url:'/regions/247/tournaments/738/international-fifa-women-s-world-cup', name:'FIFA Women\'s World Cup', sortOrder:155},{id:775, url:'/regions/247/tournaments/775/international-uefa-women-s-euro', name:'UEFA Women\'s EURO', sortOrder:156}]},
{type:0, id:103, flg:'flg-ir', name: 'Iran', tournaments: [{id:587, url:'/regions/103/tournaments/587/iran-hazfi-cup', name:'Hazfi Cup', sortOrder:0},{id:279, url:'/regions/103/tournaments/279/iran-persian-gulf-pro-league', name:'Persian Gulf Pro League', sortOrder:0},{id:534, url:'/regions/103/tournaments/534/iran-azadegan-league', name:'Azadegan League', sortOrder:0}]},
{type:0, id:104, flg:'flg-iq', name: 'Iraq', tournaments: [{id:384, url:'/regions/104/tournaments/384/iraq-super-league', name:'Super League', sortOrder:0}]},
{type:0, id:105, flg:'flg-ie', name: 'Ireland', tournaments: [{id:116, url:'/regions/105/tournaments/116/ireland-fai-cup', name:'FAI Cup', sortOrder:0},{id:197, url:'/regions/105/tournaments/197/ireland-first-division', name:'First Division', sortOrder:0},{id:141, url:'/regions/105/tournaments/141/ireland-league-cup', name:'League Cup', sortOrder:0},{id:113, url:'/regions/105/tournaments/113/ireland-premier-division', name:'Premier Division', sortOrder:0},{id:220, url:'/regions/105/tournaments/220/ireland-premier-division-qualification', name:'Premier Division Qualification', sortOrder:0},{id:566, url:'/regions/105/tournaments/566/ireland-super-cup', name:'Super Cup', sortOrder:0}]},
{type:0, id:107, flg:'flg-il', name: 'Israel', tournaments: [{id:181, url:'/regions/107/tournaments/181/israel-liga-leumit', name:'Liga Leumit', sortOrder:0},{id:97, url:'/regions/107/tournaments/97/israel-ligat-ha-al', name:'Ligat ha\'Al', sortOrder:0},{id:400, url:'/regions/107/tournaments/400/israel-toto-cup-ligat-al', name:'Toto Cup Ligat Al', sortOrder:0}]},
{type:0, id:108, flg:'flg-it', name: 'Italy', tournaments: [{id:60, url:'/regions/108/tournaments/60/italy-coppa-italia', name:'Coppa Italia', sortOrder:26},{id:64, url:'/regions/108/tournaments/64/italy-supercoppa-italiana', name:'Supercoppa Italiana', sortOrder:26},{id:5, url:'/regions/108/tournaments/5/italy-serie-a', name:'Serie A', sortOrder:180},{id:106, url:'/regions/108/tournaments/106/italy-serie-c', name:'Serie C', sortOrder:0},{id:435, url:'/regions/108/tournaments/435/italy-serie-d', name:'Serie D', sortOrder:0},{id:742, url:'/regions/108/tournaments/742/italy-serie-a-femminile', name:'Serie A Femminile', sortOrder:3},{id:19, url:'/regions/108/tournaments/19/italy-serie-b', name:'Serie B', sortOrder:10}]},
{type:0, id:109, flg:'flg-jm', name: 'Jamaica', tournaments: [{id:366, url:'/regions/109/tournaments/366/jamaica-premier-league', name:'Premier League', sortOrder:0}]},
{type:0, id:110, flg:'flg-jp', name: 'Japan', tournaments: [{id:358, url:'/regions/110/tournaments/358/japan-cup', name:'Cup', sortOrder:0},{id:324, url:'/regions/110/tournaments/324/japan-j-league-2', name:'J. League 2', sortOrder:0},{id:186, url:'/regions/110/tournaments/186/japan-league-cup', name:'League Cup', sortOrder:0},{id:150, url:'/regions/110/tournaments/150/japan-j-league', name:'J- League', sortOrder:10},{id:248, url:'/regions/110/tournaments/248/japan-super-cup', name:'Super Cup', sortOrder:10},{id:599, url:'/regions/110/tournaments/599/japan-football-league', name:'Football League', sortOrder:0}]},
{type:0, id:112, flg:'flg-jo', name: 'Jordan', tournaments: [{id:284, url:'/regions/112/tournaments/284/jordan-1-division', name:'1. Division', sortOrder:0}]},
{type:0, id:113, flg:'flg-kz', name: 'Kazakhstan', tournaments: [{id:614, url:'/regions/113/tournaments/614/kazakhstan-cup', name:'Cup', sortOrder:0},{id:153, url:'/regions/113/tournaments/153/kazakhstan-premier-league', name:'Premier League', sortOrder:0},{id:604, url:'/regions/113/tournaments/604/kazakhstan-super-cup', name:'Super Cup', sortOrder:0},{id:558, url:'/regions/113/tournaments/558/kazakhstan-premier-league-qualification', name:'Premier League Qualification', sortOrder:0}]},
{type:0, id:114, flg:'flg-ke', name: 'Kenya', tournaments: [{id:355, url:'/regions/114/tournaments/355/kenya-premier-league', name:'Premier League', sortOrder:0}]},
{type:0, id:118, flg:'flg-kw', name: 'Kuwait', tournaments: [{id:293, url:'/regions/118/tournaments/293/kuwait-1-division', name:'1. Division', sortOrder:0}]},
{type:0, id:121, flg:'flg-lv', name: 'Latvia', tournaments: [{id:624, url:'/regions/121/tournaments/624/latvia-super-cup', name:'Super Cup', sortOrder:0},{id:155, url:'/regions/121/tournaments/155/latvia-virsliga', name:'Virsliga', sortOrder:0}]},
{type:0, id:127, flg:'flg-lt', name: 'Lithuania', tournaments: [{id:159, url:'/regions/127/tournaments/159/lithuania-a-lyga', name:'A Lyga', sortOrder:0},{id:625, url:'/regions/127/tournaments/625/lithuania-cup', name:'Cup', sortOrder:0},{id:593, url:'/regions/127/tournaments/593/lithuania-super-cup', name:'Super Cup', sortOrder:0},{id:652, url:'/regions/127/tournaments/652/lithuania-a-lyga-qualification', name:'A Lyga Qualification', sortOrder:0}]},
{type:0, id:128, flg:'flg-lu', name: 'Luxembourg', tournaments: [{id:172, url:'/regions/128/tournaments/172/luxembourg-1-division', name:'1. Division', sortOrder:0},{id:452, url:'/regions/128/tournaments/452/luxembourg-1-division-qualification', name:'1. Division Qualification', sortOrder:0},{id:626, url:'/regions/128/tournaments/626/luxembourg-luxembourg-cup-1', name:'Luxembourg Cup 1', sortOrder:0}]},
{type:0, id:130, flg:'flg-mk', name: 'Macedonia', tournaments: [{id:627, url:'/regions/130/tournaments/627/macedonia-cup', name:'Cup', sortOrder:0},{id:396, url:'/regions/130/tournaments/396/macedonia-vtora-liga', name:'Vtora Liga', sortOrder:0},{id:453, url:'/regions/130/tournaments/453/macedonia-prva-liga-qualification', name:'Prva Liga Qualification', sortOrder:0}]},
{type:0, id:133, flg:'flg-my', name: 'Malaysia', tournaments: [{id:609, url:'/regions/133/tournaments/609/malaysia-premier-league', name:'Premier League', sortOrder:0},{id:336, url:'/regions/133/tournaments/336/malaysia-super-liga', name:'Super Liga', sortOrder:0}]},
{type:0, id:136, flg:'flg-mt', name: 'Malta', tournaments: [{id:410, url:'/regions/136/tournaments/410/malta-1-division', name:'1. Division', sortOrder:0},{id:628, url:'/regions/136/tournaments/628/malta-cup', name:'Cup', sortOrder:0},{id:184, url:'/regions/136/tournaments/184/malta-premier-league', name:'Premier League', sortOrder:0}]},
{type:0, id:142, flg:'flg-mx', name: 'Mexico', tournaments: [{id:532, url:'/regions/142/tournaments/532/mexico-copa-mx', name:'Copa MX', sortOrder:0},{id:326, url:'/regions/142/tournaments/326/mexico-liga-de-expansión-mx', name:'Liga de Expansión MX', sortOrder:0},{id:588, url:'/regions/142/tournaments/588/mexico-liga-premier', name:'Liga Premier', sortOrder:0},{id:103, url:'/regions/142/tournaments/103/mexico-liga-mx', name:'Liga MX', sortOrder:10}]},
{type:0, id:144, flg:'flg-md', name: 'Moldova', tournaments: [{id:629, url:'/regions/144/tournaments/629/moldova-cup', name:'Cup', sortOrder:0},{id:178, url:'/regions/144/tournaments/178/moldova-super-liga', name:'Super Liga', sortOrder:0}]},
{type:0, id:147, flg:'flg-me', name: 'Montenegro', tournaments: [{id:235, url:'/regions/147/tournaments/235/montenegro-1-division', name:'1. Division', sortOrder:0},{id:454, url:'/regions/147/tournaments/454/montenegro-1-division-playoff', name:'1. Division Playoff', sortOrder:0},{id:412, url:'/regions/147/tournaments/412/montenegro-2-division', name:'2. Division', sortOrder:0},{id:630, url:'/regions/147/tournaments/630/montenegro-montenegro-cup-1', name:'Montenegro Cup 1', sortOrder:0}]},
{type:0, id:149, flg:'flg-ma', name: 'Morocco', tournaments: [{id:291, url:'/regions/149/tournaments/291/morocco-botola-pro', name:'Botola Pro', sortOrder:0},{id:523, url:'/regions/149/tournaments/523/morocco-botola-pro-2', name:'Botola Pro 2', sortOrder:0}]},
{type:0, id:155, flg:'flg-nl', name: 'Netherlands', tournaments: [{id:120, url:'/regions/155/tournaments/120/netherlands-dutch-super-cup', name:'Dutch Super Cup', sortOrder:22},{id:47, url:'/regions/155/tournaments/47/netherlands-knvb-cup', name:'KNVB Cup', sortOrder:22},{id:13, url:'/regions/155/tournaments/13/netherlands-eredivisie', name:'Eredivisie', sortOrder:110},{id:66, url:'/regions/155/tournaments/66/netherlands-eerste-divisie', name:'Eerste Divisie', sortOrder:0},{id:714, url:'/regions/155/tournaments/714/netherlands-eredivisie-comeback', name:'Eredivisie Comeback', sortOrder:0},{id:457, url:'/regions/155/tournaments/457/netherlands-tweede-divisie', name:'Tweede Divisie', sortOrder:0},{id:88, url:'/regions/155/tournaments/88/netherlands-eredivisie-promotion-playoff', name:'Eredivisie Promotion Playoff', sortOrder:10}]},
{type:0, id:158, flg:'flg-nz', name: 'New Zealand', tournaments: [{id:303, url:'/regions/158/tournaments/303/new-zealand-premier-league', name:'Premier League', sortOrder:0}]},
{type:0, id:161, flg:'flg-ng', name: 'Nigeria', tournaments: [{id:294, url:'/regions/161/tournaments/294/nigeria-1-division', name:'1. Division', sortOrder:0}]},
{type:1, id:264, flg:'flg-cna', name: 'North & Central America', tournaments: [{id:222, url:'/regions/264/tournaments/222/north-central-america-concacaf-champions-cup', name:'CONCACAF Champions Cup', sortOrder:12},{id:131, url:'/regions/264/tournaments/131/north-central-america-concacaf-gold-cup', name:'CONCACAF Gold Cup', sortOrder:25},{id:752, url:'/regions/264/tournaments/752/north-central-america-concacaf-gold-cup-qualification', name:'CONCACAF Gold Cup Qualification', sortOrder:0},{id:756, url:'/regions/264/tournaments/756/north-central-america-concacaf-nations-league-qualification', name:'CONCACAF Nations League Qualification', sortOrder:0},{id:668, url:'/regions/264/tournaments/668/north-central-america-concacaf-league', name:'CONCACAF League', sortOrder:1},{id:740, url:'/regions/264/tournaments/740/north-central-america-leagues-cup', name:'Leagues Cup', sortOrder:10},{id:462, url:'/regions/264/tournaments/462/north-central-america-cfu-club-champions-cup', name:'CFU Club Champions Cup', sortOrder:0},{id:655, url:'/regions/264/tournaments/655/north-central-america-concacaf-championship-u20', name:'CONCACAF Championship U20', sortOrder:0}]},
{type:0, id:258, flg:'flg-gb-nir', name: 'N. Ireland', tournaments: [{id:446, url:'/regions/258/tournaments/446/n-ireland-championship', name:'Championship', sortOrder:0},{id:545, url:'/regions/258/tournaments/545/n-ireland-irish-cup', name:'Irish Cup', sortOrder:0},{id:328, url:'/regions/258/tournaments/328/n-ireland-league-cup', name:'League Cup', sortOrder:0},{id:126, url:'/regions/258/tournaments/126/n-ireland-premiership', name:'Premiership', sortOrder:0},{id:329, url:'/regions/258/tournaments/329/n-ireland-premiership-qualification', name:'Premiership Qualification', sortOrder:0}]},
{type:0, id:165, flg:'flg-no', name: 'Norway', tournaments: [{id:41, url:'/regions/165/tournaments/41/norway-eliteserien', name:'Eliteserien', sortOrder:10},{id:50, url:'/regions/165/tournaments/50/norway-1-division', name:'1. Division', sortOrder:0},{id:681, url:'/regions/165/tournaments/681/norway-1-division-qualification', name:'1. Division Qualification', sortOrder:0},{id:200, url:'/regions/165/tournaments/200/norway-2-division', name:'2. Division', sortOrder:0},{id:52, url:'/regions/165/tournaments/52/norway-cup', name:'Cup', sortOrder:0},{id:99, url:'/regions/165/tournaments/99/norway-eliteserien-qualification', name:'Eliteserien Qualification', sortOrder:10}]},
{type:0, id:166, flg:'flg-om', name: 'Oman', tournaments: [{id:304, url:'/regions/166/tournaments/304/oman-professional-league', name:'Professional League', sortOrder:0}]},
{type:0, id:172, flg:'flg-py', name: 'Paraguay', tournaments: [{id:422, url:'/regions/172/tournaments/422/paraguay-division-intermedia', name:'Division Intermedia', sortOrder:0},{id:246, url:'/regions/172/tournaments/246/paraguay-primera-division', name:'Primera Division', sortOrder:0}]},
{type:0, id:173, flg:'flg-pe', name: 'Peru', tournaments: [{id:687, url:'/regions/173/tournaments/687/peru-copa-peru', name:'Copa Peru', sortOrder:0},{id:195, url:'/regions/173/tournaments/195/peru-primera-division', name:'Primera Division', sortOrder:0}]},
{type:0, id:176, flg:'flg-pl', name: 'Poland', tournaments: [{id:101, url:'/regions/176/tournaments/101/poland-cup', name:'Cup', sortOrder:0},{id:232, url:'/regions/176/tournaments/232/poland-i-liga', name:'I Liga', sortOrder:0},{id:311, url:'/regions/176/tournaments/311/poland-ii-liga', name:'II Liga', sortOrder:0},{id:76, url:'/regions/176/tournaments/76/poland-ekstraklasa', name:'Ekstraklasa', sortOrder:10},{id:231, url:'/regions/176/tournaments/231/poland-super-cup', name:'Super Cup', sortOrder:10}]},
{type:0, id:177, flg:'flg-pt', name: 'Portugal', tournaments: [{id:122, url:'/regions/177/tournaments/122/portugal-super-cup', name:'Super Cup', sortOrder:23},{id:11, url:'/regions/177/tournaments/11/portugal-taça-de-portugal', name:'Taça de Portugal', sortOrder:23},{id:21, url:'/regions/177/tournaments/21/portugal-liga-portugal', name:'Liga Portugal', sortOrder:120},{id:414, url:'/regions/177/tournaments/414/portugal-liga-3', name:'Liga 3', sortOrder:0},{id:139, url:'/regions/177/tournaments/139/portugal-liga-portugal-2', name:'Liga Portugal 2', sortOrder:0},{id:275, url:'/regions/177/tournaments/275/portugal-taça-da-liga', name:'Taça da Liga', sortOrder:10}]},
{type:0, id:179, flg:'flg-qa', name: 'Qatar', tournaments: [{id:285, url:'/regions/179/tournaments/285/qatar-stars-league', name:'Stars League', sortOrder:10},{id:658, url:'/regions/179/tournaments/658/qatar-stars-league-qualification', name:'Stars League Qualification', sortOrder:10}]},
{type:0, id:181, flg:'flg-ro', name: 'Romania', tournaments: [{id:145, url:'/regions/181/tournaments/145/romania-cup', name:'Cup', sortOrder:0},{id:415, url:'/regions/181/tournaments/415/romania-liga-ii', name:'Liga II', sortOrder:0},{id:213, url:'/regions/181/tournaments/213/romania-super-cup', name:'Super Cup', sortOrder:0},{id:121, url:'/regions/181/tournaments/121/romania-superliga', name:'Superliga', sortOrder:0},{id:647, url:'/regions/181/tournaments/647/romania-superliga-qualification', name:'Superliga Qualification', sortOrder:0}]},
{type:0, id:182, flg:'flg-ru', name: 'Russia', tournaments: [{id:111, url:'/regions/182/tournaments/111/russia-cup', name:'Cup', sortOrder:10},{id:127, url:'/regions/182/tournaments/127/russia-super-cup', name:'Super Cup', sortOrder:10},{id:77, url:'/regions/182/tournaments/77/russia-premier-league', name:'Premier League', sortOrder:70},{id:257, url:'/regions/182/tournaments/257/russia-first-league', name:'First League', sortOrder:0},{id:527, url:'/regions/182/tournaments/527/russia-premier-league-qualification', name:'Premier League Qualification', sortOrder:10}]},
{type:0, id:192, flg:'flg-sm', name: 'San Marino', tournaments: [{id:331, url:'/regions/192/tournaments/331/san-marino-campionato', name:'Campionato', sortOrder:0}]},
{type:0, id:194, flg:'flg-sa', name: 'Saudi Arabia', tournaments: [{id:282, url:'/regions/194/tournaments/282/saudi-arabia-pro-league', name:'Pro League', sortOrder:10}]},
{type:0, id:253, flg:'flg-gb-sct', name: 'Scotland', tournaments: [{id:10, url:'/regions/253/tournaments/10/scotland-fa-cup', name:'FA Cup', sortOrder:10},{id:20, url:'/regions/253/tournaments/20/scotland-premiership', name:'Premiership', sortOrder:60},{id:118, url:'/regions/253/tournaments/118/scotland-challenge-cup', name:'Challenge Cup', sortOrder:0},{id:71, url:'/regions/253/tournaments/71/scotland-championship', name:'Championship', sortOrder:0},{id:72, url:'/regions/253/tournaments/72/scotland-league-one', name:'League One', sortOrder:0},{id:73, url:'/regions/253/tournaments/73/scotland-league-two', name:'League Two', sortOrder:0},{id:25, url:'/regions/253/tournaments/25/scotland-league-cup', name:'League Cup', sortOrder:10},{id:225, url:'/regions/253/tournaments/225/scotland-premiership-qualification', name:'Premiership Qualification', sortOrder:10},{id:676, url:'/regions/253/tournaments/676/scotland-championship-qualification', name:'Championship Qualification', sortOrder:0},{id:677, url:'/regions/253/tournaments/677/scotland-league-one-qualification', name:'League One Qualification', sortOrder:0},{id:678, url:'/regions/253/tournaments/678/scotland-league-two-qualification', name:'League Two Qualification', sortOrder:0},{id:637, url:'/regions/253/tournaments/637/scotland-scotland-highland-lowland', name:'Scotland Highland/Lowland', sortOrder:0}]},
{type:0, id:196, flg:'flg-rs', name: 'Serbia', tournaments: [{id:112, url:'/regions/196/tournaments/112/serbia-cup', name:'Cup', sortOrder:0},{id:416, url:'/regions/196/tournaments/416/serbia-prva-liga', name:'Prva Liga', sortOrder:0},{id:80, url:'/regions/196/tournaments/80/serbia-super-liga', name:'Super Liga', sortOrder:10}]},
{type:0, id:199, flg:'flg-sg', name: 'Singapore', tournaments: [{id:443, url:'/regions/199/tournaments/443/singapore-cup', name:'Cup', sortOrder:0},{id:254, url:'/regions/199/tournaments/254/singapore-s-league', name:'S.League', sortOrder:0}]},
{type:0, id:200, flg:'flg-sk', name: 'Slovakia', tournaments: [{id:323, url:'/regions/200/tournaments/323/slovakia-2-liga', name:'2. Liga', sortOrder:0},{id:107, url:'/regions/200/tournaments/107/slovakia-fa-cup', name:'FA Cup', sortOrder:0},{id:130, url:'/regions/200/tournaments/130/slovakia-super-cup', name:'Super Cup', sortOrder:0},{id:74, url:'/regions/200/tournaments/74/slovakia-super-liga', name:'Super Liga', sortOrder:0}]},
{type:0, id:201, flg:'flg-si', name: 'Slovenia', tournaments: [{id:417, url:'/regions/201/tournaments/417/slovenia-2-division', name:'2. Division', sortOrder:0},{id:108, url:'/regions/201/tournaments/108/slovenia-cup', name:'Cup', sortOrder:0},{id:79, url:'/regions/201/tournaments/79/slovenia-prva-liga', name:'Prva Liga', sortOrder:0},{id:272, url:'/regions/201/tournaments/272/slovenia-prva-liga-qualification', name:'Prva Liga Qualification', sortOrder:0}]},
{type:0, id:204, flg:'flg-za', name: 'South Africa', tournaments: [{id:579, url:'/regions/204/tournaments/579/south-africa-cup', name:'Cup', sortOrder:0},{id:278, url:'/regions/204/tournaments/278/south-africa-premier-soccer-league', name:'Premier Soccer League', sortOrder:0},{id:580, url:'/regions/204/tournaments/580/south-africa-mtn-8-cup', name:'MTN 8 Cup', sortOrder:0},{id:525, url:'/regions/204/tournaments/525/south-africa-national-first-division', name:'National First Division', sortOrder:0}]},
{type:1, id:265, flg:'flg-csa', name: 'South America', tournaments: [{id:271, url:'/regions/265/tournaments/271/south-america-recopa-sudamericana', name:'Recopa Sudamericana', sortOrder:11},{id:146, url:'/regions/265/tournaments/146/south-america-copa-sudamericana', name:'Copa Sudamericana', sortOrder:12},{id:105, url:'/regions/265/tournaments/105/south-america-copa-libertadores', name:'Copa Libertadores', sortOrder:21},{id:761, url:'/regions/265/tournaments/761/south-america-copa-libertadores-qualification', name:'Copa Libertadores Qualification', sortOrder:0},{id:764, url:'/regions/265/tournaments/764/south-america-copa-sudamericana-qualification', name:'Copa Sudamericana Qualification', sortOrder:0}]},
{type:0, id:260, flg:'flg-kr', name: 'South Korea', tournaments: [{id:641, url:'/regions/260/tournaments/641/south-korea-cup', name:'Cup', sortOrder:0},{id:418, url:'/regions/260/tournaments/418/south-korea-k-league-2', name:'K League 2', sortOrder:0},{id:634, url:'/regions/260/tournaments/634/south-korea-k3-league', name:'K3 League', sortOrder:0},{id:387, url:'/regions/260/tournaments/387/south-korea-k-league-1', name:'K League 1', sortOrder:10},{id:560, url:'/regions/260/tournaments/560/south-korea-k-league-1-qualification', name:'K-League 1 Qualification', sortOrder:10}]},
{type:0, id:206, flg:'flg-es', name: 'Spain', tournaments: [{id:14, url:'/regions/206/tournaments/14/spain-copa-del-rey', name:'Copa del Rey', sortOrder:27},{id:61, url:'/regions/206/tournaments/61/spain-supercopa-de-espana', name:'Supercopa de Espana', sortOrder:27},{id:4, url:'/regions/206/tournaments/4/spain-laliga', name:'LaLiga', sortOrder:190},{id:318, url:'/regions/206/tournaments/318/spain-primera-division-rfef', name:'Primera Division RFEF', sortOrder:0},{id:744, url:'/regions/206/tournaments/744/spain-liga-f', name:'Liga F', sortOrder:4},{id:63, url:'/regions/206/tournaments/63/spain-segunda-división', name:'Segunda División', sortOrder:10}]},
{type:0, id:212, flg:'flg-se', name: 'Sweden', tournaments: [{id:40, url:'/regions/212/tournaments/40/sweden-allsvenskan', name:'Allsvenskan', sortOrder:10},{id:158, url:'/regions/212/tournaments/158/sweden-2-division', name:'2. Division', sortOrder:0},{id:42, url:'/regions/212/tournaments/42/sweden-cup', name:'Cup', sortOrder:0},{id:48, url:'/regions/212/tournaments/48/sweden-superettan', name:'Superettan', sortOrder:0},{id:310, url:'/regions/212/tournaments/310/sweden-superettan-qualification', name:'Superettan Qualification', sortOrder:0},{id:98, url:'/regions/212/tournaments/98/sweden-allsvenskan-qualification', name:'Allsvenskan qualification', sortOrder:10},{id:439, url:'/regions/212/tournaments/439/sweden-1-division', name:'1. Division', sortOrder:0},{id:653, url:'/regions/212/tournaments/653/sweden-1-division-qualification', name:'1. Division Qualification', sortOrder:0}]},
{type:0, id:213, flg:'flg-ch', name: 'Switzerland', tournaments: [{id:55, url:'/regions/213/tournaments/55/switzerland-challenge-league', name:'Challenge League', sortOrder:0},{id:45, url:'/regions/213/tournaments/45/switzerland-switzerland-cup', name:'Switzerland Cup', sortOrder:0},{id:33, url:'/regions/213/tournaments/33/switzerland-super-league', name:'Super League', sortOrder:10},{id:163, url:'/regions/213/tournaments/163/switzerland-super-league-qualification', name:'Super League Qualification', sortOrder:10},{id:461, url:'/regions/213/tournaments/461/switzerland-1-liga', name:'1.Liga', sortOrder:0},{id:529, url:'/regions/213/tournaments/529/switzerland-promotion-league', name:'Promotion League', sortOrder:0}]},
{type:0, id:214, flg:'flg-sy', name: 'Syria', tournaments: [{id:296, url:'/regions/214/tournaments/296/syria-1-division', name:'1. Division', sortOrder:0}]},
{type:0, id:215, flg:'flg-tw', name: 'Taiwan', tournaments: [{id:337, url:'/regions/215/tournaments/337/taiwan-division-a', name:'Division A', sortOrder:0}]},
{type:0, id:217, flg:'flg-tz', name: 'Tanzania', tournaments: [{id:382, url:'/regions/217/tournaments/382/tanzania-premier-league', name:'Premier League', sortOrder:0}]},
{type:0, id:218, flg:'flg-th', name: 'Thailand', tournaments: [{id:335, url:'/regions/218/tournaments/335/thailand-thai-league', name:'Thai League', sortOrder:0},{id:598, url:'/regions/218/tournaments/598/thailand-thai-league-2', name:'Thai League 2', sortOrder:0}]},
{type:0, id:224, flg:'flg-tn', name: 'Tunisia', tournaments: [{id:276, url:'/regions/224/tournaments/276/tunisia-ligue-1', name:'Ligue 1', sortOrder:0},{id:663, url:'/regions/224/tournaments/663/tunisia-ligue-i-qualification', name:'Ligue I Qualification', sortOrder:0}]},
{type:0, id:225, flg:'flg-tr', name: 'Turkey', tournaments: [{id:44, url:'/regions/225/tournaments/44/turkey-cup', name:'Cup', sortOrder:10},{id:233, url:'/regions/225/tournaments/233/turkey-super-cup', name:'Super Cup', sortOrder:10},{id:17, url:'/regions/225/tournaments/17/turkey-super-lig', name:'Super Lig', sortOrder:100},{id:140, url:'/regions/225/tournaments/140/turkey-1-lig', name:'1. Lig', sortOrder:0},{id:280, url:'/regions/225/tournaments/280/turkey-2-lig', name:'2. Lig', sortOrder:0},{id:327, url:'/regions/225/tournaments/327/turkey-3-lig', name:'3. Lig', sortOrder:0}]},
{type:0, id:231, flg:'flg-ae', name: 'U.A.E.', tournaments: [{id:295, url:'/regions/231/tournaments/295/u-a-e-pro-league', name:'Pro League', sortOrder:0}]},
{type:0, id:229, flg:'flg-ug', name: 'Uganda', tournaments: [{id:371, url:'/regions/229/tournaments/371/uganda-super-league', name:'Super League', sortOrder:0}]},
{type:0, id:230, flg:'flg-ua', name: 'Ukraine', tournaments: [{id:125, url:'/regions/230/tournaments/125/ukraine-cup', name:'Cup', sortOrder:0},{id:114, url:'/regions/230/tournaments/114/ukraine-premier-league', name:'Premier League', sortOrder:10},{id:164, url:'/regions/230/tournaments/164/ukraine-super-cup', name:'Super Cup', sortOrder:10},{id:408, url:'/regions/230/tournaments/408/ukraine-first-league', name:'First League', sortOrder:0}]},
{type:0, id:235, flg:'flg-uy', name: 'Uruguay', tournaments: [{id:196, url:'/regions/235/tournaments/196/uruguay-primera-division', name:'Primera Division', sortOrder:0},{id:423, url:'/regions/235/tournaments/423/uruguay-segunda-division', name:'Segunda Division', sortOrder:0}]},
{type:0, id:233, flg:'flg-us', name: 'USA', tournaments: [{id:85, url:'/regions/233/tournaments/85/usa-major-league-soccer', name:'Major League Soccer', sortOrder:80},{id:322, url:'/regions/233/tournaments/322/usa-usl-championship', name:'USL Championship', sortOrder:0},{id:498, url:'/regions/233/tournaments/498/usa-usl-league-one', name:'USL League One', sortOrder:0},{id:737, url:'/regions/233/tournaments/737/usa-nwsl', name:'NWSL', sortOrder:5},{id:568, url:'/regions/233/tournaments/568/usa-us-open-cup', name:'US Open Cup', sortOrder:10}]},
{type:0, id:236, flg:'flg-uz', name: 'Uzbekistan', tournaments: [{id:251, url:'/regions/236/tournaments/251/uzbekistan-uzbek-league', name:'Uzbek League', sortOrder:0},{id:643, url:'/regions/236/tournaments/643/uzbekistan-uzbek-league-qualification', name:'Uzbek League Qualification', sortOrder:0}]},
{type:0, id:238, flg:'flg-ve', name: 'Venezuela', tournaments: [{id:237, url:'/regions/238/tournaments/237/venezuela-primera-division', name:'Primera Division', sortOrder:0},{id:420, url:'/regions/238/tournaments/420/venezuela-segunda-division', name:'Segunda Division', sortOrder:0}]},
{type:0, id:239, flg:'flg-vn', name: 'Vietnam', tournaments: [{id:392, url:'/regions/239/tournaments/392/vietnam-v-league-1', name:'V.League 1', sortOrder:0}]},
{type:0, id:254, flg:'flg-gb-wls', name: 'Wales', tournaments: [{id:138, url:'/regions/254/tournaments/138/wales-premier-league', name:'Premier League', sortOrder:0},{id:448, url:'/regions/254/tournaments/448/wales-welsh-cup', name:'Welsh Cup', sortOrder:0},{id:520, url:'/regions/254/tournaments/520/wales-championship', name:'Championship', sortOrder:0}]},
{type:0, id:245, flg:'flg-zm', name: 'Zambia', tournaments: [{id:252, url:'/regions/245/tournaments/252/zambia-1-division', name:'1. Division', sortOrder:0}]},
{type:0, id:246, flg:'flg-zw', name: 'Zimbabwe', tournaments: [{id:253, url:'/regions/246/tournaments/253/zimbabwe-1-division', name:'1. Division', sortOrder:0}]}]
"""
ALL_REGIONS = json5.loads(all_regions_raw)

class MatchScraper: # A specific crawler that is designed to be compatible with whoscored's html.
    def __init__(self, base_urls):
        self.base_urls = base_urls

    def crawl(self): #This returns the match event data in json format
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.9",
            "referer": "https://www.google.com/"
        }
        all_match_data = []
        for base_url in self.base_urls:
            try:
                response = requests.get(base_url,headers = headers, impersonate = "chrome120", timeout = 30)
                soup = BeautifulSoup(response.text, 'html.parser')
                element = soup.select_one('script:-soup-contains("matchCentreData")')
                if not element:
                    print("(!) Could not find matchCentreData script tag. (Game might not have started yet)")
                    continue

                raw_text = element.text.split("matchCentreData: ")[1].strip()
                data, _ = json.JSONDecoder().raw_decode(raw_text) #Got it converted to json format
                all_match_data.append({'data':data, 'url':base_url}) #data in json format

            except Exception as e:
                print(f"(!) Connection/Parsing error: {e}")
                continue
        return all_match_data

class LeagueScraper(MatchScraper):
    def __init__(self, league_name, league_season, country = None): #league season must be in (xxxx/yyyy) format
        #It's much better if the league country was provided.
        season_pattern = r"^(\d{4})/\d{4}$"
        name_pattern = r""
        if not re.fullmatch(season_pattern, league_season):
            raise ValueError("season must be in (xxxx/yyyy) format.")
        #If league_name not in leagues, i must call get_league on it.

        self.name = league_name
        self.season = league_season
        self.country = country
        self.session = requests.Session(impersonate="chrome120")
        super().__init__(base_urls=[])

    def all_leagues(self):#Scrape whoscored.com
        return ALL_REGIONS
    def get_league(self):  # scrapes whoscored.com -> Gets the leagues ids and names and urls out of it -> For each league it gets the years and the stage ids out of it and saves all of this in a json file named dict.json
        leagues = self.all_leagues()
        url = ""
        if self.country is not None:
            for element in leagues:
                if element['name'].lower() == self.country.lower():
                    for tournament in element['tournaments']:
                        if tournament['name'].lower() == self.name.lower():
                            url = tournament['url']
                            break
                    break

        else:
            for element in leagues:
                for tournament in element['tournaments']:
                    if tournament['name'].lower() == self.name.lower():
                        url = tournament['url']
                        break

        return url

    def get_fixtures(self):
        url = self.get_league()
        if url is  None:
            raise ValueError("Couldn't scrape whoscored.")

        full_url = "https://www.whoscored.com" + url

        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.9",
            "referer": "https://www.google.com/"
        }
        res = self.session.get(full_url, headers=headers,impersonate="chrome120",timeout=30)
        dictt = {}
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            full = soup.find(attrs = {"id" :"seasons","name":"seasons"})
            conts = full.contents
            listt = [x for x in conts if x != '\n']
            #A dictionary containing year : fixtures link. I will use the fixtures link to scrape the data out of it. Might store the resulting dictionary in a file later.
            for element in listt:
                link = "https://www.whoscored.com" + element['value']
                res1 = self.session.get(link, headers=headers, impersonate="chrome120")
                soup1 = BeautifulSoup(res1.text, 'html.parser')
                fixtures = soup1.find(attrs={"id": "link-fixtures"})
                new_element = {element.text: fixtures['href']}
                dictt.update(new_element)
        else:
            raise ValueError("nada")
        return dictt

    def get_matches(self): #Returns the list of the ids for the whole season.
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.9",
            "referer": "https://www.google.com/"
        }
        fixtures = self.get_fixtures()
        seasons = self.season.split('/')
        months_to_scrape = [
            seasons[0] + "08", seasons[0] + "09", seasons[0] + "10", seasons[0] + "11", seasons[0] + "12",
            seasons[1] + "01", seasons[1] + "02", seasons[1] + "03", seasons[1] + "04", seasons[1] + "05",
            seasons[1] + "06", seasons[1] + "07"
        ]
        my_fixture = fixtures[self.season]
        stage_id = my_fixture.split('/')[8]
        match_ids = [] #A list holding matchs ids
        for month in months_to_scrape:
            url = f"https://www.whoscored.com/tournaments/{stage_id}/data/?d={month}"
            try:
                response = requests.get(url, headers = headers, impersonate="chrome120", timeout=30)
                data = response.json()
                for tourney in data.get('tournaments', []):
                    for match in tourney.get('matches', []):
                        match_ids.append(match['id'])
            except Exception as e:
                print(f"(!) Error fetching schedule for month: {month},{e}")
        return match_ids

    def get_data(self):
        match_ids = self.get_matches()
        urls_to_scrape = []
        for match_id in match_ids:
            url = f"https://www.whoscored.com/Matches/{match_id}/Live"
            urls_to_scrape.append(url)
        self.base_urls = urls_to_scrape
        return self.crawl()

    def save(self, path="../data/events"):  # --> Polymorph behavior
        combined_df = pd.DataFrame()
        data_list = self.get_data()

        for data_point in data_list:
            url = data_point['url']
            data = data_point['data']

            # WhoScored JSON uses camelCase 'teamId'
            home_team_id = int(data['home']['teamId'])
            home_team_name = data['home']['name']
            away_team_id = int(data['away']['teamId'])
            away_team_name = data['away']['name']

            teams = {
                home_team_id: home_team_name,
                away_team_id: away_team_name
            }

            id, league, season = get_infos(url)
            players_names = data['playerIdNameDictionary']
            evs = data.get('events', [])

            df = pd.DataFrame(evs)
            if df.empty:
                continue

            df['team_name'] = df['teamId'].map(teams)

            df['player_name'] = df['playerId'].dropna().astype(int).astype(str).map(players_names)

            df['game_id'] = id

            combined_df = pd.concat(
                [combined_df, df],
                ignore_index=True
            )

        if not combined_df.empty:
            combined_df.to_parquet(
                path,
                engine='pyarrow',
                compression='snappy',
                partition_cols=['game_id']
            )
            print(f"Successfully saved {len(combined_df)} raw events partitioned to {path}")


def get_infos(url):
    pattern = re.compile(r'matches/(\d+)/.*?/[^-]+-(.+?)-(\d{4}-\d{4})')
    match = pattern.search(url)
    id, league, season = "", "",""
    if match:
        id, league, season = match.group(1), match.group(2),match.group(3)
    return id, league, season

class SpadlConverter:
    def __init__(self,data_list, combined_df = None): #The input data must be in JSON format
        self.data_list = data_list
        self.combined_df = combined_df

    def parse(self):
        for data_point in self.data_list: #data point is in the format data,url of the match.
            url = data_point['url']
            data = data_point['data']
            home_team_id = int(data['home']['teamId'])
            home_team_name = (data['home']['name'])
            away_team_id = int(data['away']['teamId'])
            away_team_name = (data['away']['name'])
            teams = {
                home_team_id: home_team_name,
                away_team_id: away_team_name
            }
            id,league,season = (get_infos(url))
            temp_file = tempfile.NamedTemporaryFile(mode = 'w', suffix = '.json', delete = False)
            temp_path = temp_file.name
            json.dump(data, temp_file)
            temp_file.close()
            parser = WhoScoredParser(
                path = temp_path,
                competition_id = league,
                season_id = season,
                game_id = int(id),
            )
            df_events = pd.DataFrame.from_dict(parser.extract_events(), orient="index")
            df_events = df_events.merge(_eventtypesdf, on="type_id", how="left").reset_index(drop=True)
            df_spadl = convert_to_actions(df_events, home_team_id=home_team_id)
            df_spadl = pd.merge(df_spadl, spadlconfig.actiontypes_df(), on='type_id', how='inner') #added action name
            df_spadl = pd.merge(df_spadl, spadlconfig.results_df(), on='result_id', how='inner') #added result name
            df_spadl = pd.merge(df_spadl, spadlconfig.bodyparts_df(), on='bodypart_id', how='inner') ##added body part name
            players_names = data['playerIdNameDictionary']
            df_spadl['player_id'] = df_spadl['player_id'].apply(lambda x: int(x))
            df_spadl['player_id'] = df_spadl['player_id'].apply(lambda x: str(x))
            df_spadl['player_name'] = df_spadl['player_id'].map(players_names)
            df_spadl['team_name'] = df_spadl['team_id'].map(teams)
            self.combined_df = pd.concat(
                [self.combined_df, df_spadl],
                ignore_index=True
            )
        return self.combined_df

    def save(self, path = "../data/spadl"):
        self.combined_df.to_parquet(
            path,
            engine='pyarrow',
            compression='snappy',
            partition_cols=['game_id']
        )

class GstatesConverter:
    features_list = [
        fs.actiontype,
        fs.actiontype_onehot,
        fs.bodypart,
        fs.bodypart_onehot,
        fs.result,
        fs.result_onehot,
        fs.goalscore,
        fs.startlocation,
        fs.endlocation,
        fs.movement,
        fs.space_delta,
        fs.startpolar,
        fs.endpolar,
        fs.team,
        fs.time,
        fs.time_delta
    ]
    labels_list = [
        lab.scores,
        lab.concedes,
        lab.goal_from_shot
    ]
    def __init__(self,read_path = "../data/spadl", columns = None, filters = None):
        self.data = pd.read_parquet(
            read_path,
            engine='pyarrow',
            filters = filters #To filter out games by their ids.(ex: filters=[('game_id', '=', 1914251)])
        )
        cat_cols = self.data.select_dtypes(include=['category']).columns
        self.data[cat_cols] = self.data[cat_cols].astype('object') #converting game_id to string.
        unique_teams = self.data['team_id'].unique()
        self.home_team_id = unique_teams[0]
        if self.data is not None:
            print(f"The data of {len(self.data)} games loaded.")

    def convert_to_gamestate(self,match_data,home_team,nbr_of_previous_actions = 3, normalize = True): #Normalization stands for performing all action in the same playing direction
        gs = fs.gamestates(match_data, nb_prev_actions=nbr_of_previous_actions)
        if normalize:
            gamestates = fs.play_left_to_right(gs, home_team)
        return gamestates

    def compute_features(self,match_data,home_team, features = features_list):
        gs = self.convert_to_gamestate(match_data, home_team)
        X = pd.concat([fn(gs) for fn in features], axis=1)
        X = pd.concat([X, match_data['game_id']], axis=1)
        return X
    def compute_labels(self,match_data, labels = labels_list):
        Y = pd.concat([fn(match_data) for fn in labels], axis=1)
        Y = pd.concat([Y, match_data['game_id']], axis=1)
        return Y

    def convert(self, features=features_list, labels=labels_list):
        all_features = []
        all_labels = []
        all_is_shot = []  # List to hold our new shot masks

        for game_id, game_data in self.data.groupby('game_id'):
            home_team_id = game_data['team_id'].values[0]

            X = self.compute_features(game_data, home_team_id)
            Y = self.compute_labels(game_data)

            # Create the 'is_shot' column (1 if it's a shot of any kind, 0 otherwise)
            is_shot = game_data['type_name'].str.contains('shot', case=False, na=False).astype(int)
            is_shot.name = 'is_shot'

            all_features.append(X)
            all_labels.append(Y)
            all_is_shot.append(is_shot)

        X_final = pd.concat(all_features)
        Y_final = pd.concat(all_labels)
        is_shot_final = pd.concat(all_is_shot)

        result = pd.concat([X_final, Y_final, is_shot_final], axis=1)
        result = result.loc[:, ~result.columns.duplicated()].copy()

        return result
    def save(self, path="../data/game_states"):
        res = self.convert()
        res.to_parquet(
            path,
            engine='pyarrow',
            compression='snappy',
            partition_cols=['game_id']
        )

def main():
    list = ["https://www.whoscored.com/matches/1914256/live/spain-laliga-2025-2026-real-madrid-athletic-club", "https://www.whoscored.com/matches/1914251/live/spain-laliga-2025-2026-sevilla-real-madrid"]
    scr = MatchScraper(list)
    data = scr.crawl()
    #lg = LeagueScraper("laliga","2025/2026","spain")
    #lg.save()
    #cv = SpadlConverter(data_list = data)
    #dff = cv.parse()

    #cv.save()
    gss = GstatesConverter()
    gss.save()
if __name__ == "__main__":
    main()