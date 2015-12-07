import json
data = []

with open('RottenTomatoes-MovieInfo.json') as f:
    for line in f:
        data.append(json.loads(line))

s = open('test','w')

for d in data:
  mid = d['id']
  name = d['title']
  year = d['year']
  critic_rating = d['ratings']['critics_score']
  audience_rating = d['ratings']['audience_score']
  runtime = d['runtime']
  image_url = d['posters']['detailed']
  string = "INSERT INTO Movie VALUES(" + str(mid) + ',' + str(name) + ',' + "null" + ',' + str(year) + ',' + str(critic_rating) + ',' + str(audience_rating) + ',' + str(runtime) + ',' + str(image_url) + ");"
  s.write(string)
  s.write('\n')

s.close()






  name varchar(255),
  description varchar(255),
  year varchar(255),
  critic_rating INTEGER,
  audience_rating INTEGER,
  runtime INTEGER,
  image_url varchar(255),
