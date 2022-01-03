G52AGL-YJVQ32-5FL5Q2


9. 12. 19. 25. 27. 28. 29. 37. 44.  46. 47. 60. 62. 64
9. 12. 19. 25. 27. 28. 29. 37. 44.  46. 47. 60. 62. 64


db.createUser(
  {
    user: "useradmin",
    pwd: "ThinhMinh1234",
    roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
  }
)

db.createUser(
  {
    user: "minh",
    pwd: "ThinhMinh1234",
    roles: [ { role: "readWrite", db: "minh" } ]
  }

client = MongoClient("mongodb://minh:ThinhMinh1234@45.77.38.64:27017/?authSource=minh")