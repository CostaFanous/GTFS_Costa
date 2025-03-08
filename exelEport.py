import psycopg2
import json
import csv

# נתיב הקובץ CSV שבו נמצאת רשימת ה-Route ID ושמות הקבצים
csv_file_path = "C:/Users/Costa/Desktop/GEOJSON/Route.csv"

# התחברות למסד הנתונים
conn = psycopg2.connect(
    host="localhost",
    database="Gtfs",
    user="postgres",
    password="123"
)
cursor = conn.cursor()

# קריאת רשימת המסלולים מקובץ ה-CSV
routes = []
with open(csv_file_path, "r", encoding="utf-8") as csv_file:
    reader = csv.reader(csv_file)
    next(reader)  # דילוג על שורת הכותרות
    for row in reader:
        route_id = row[0].strip()  # עמודה A - מספר המסלול
        file_name = row[1].strip()  # עמודה B - שם הקובץ הרצוי
        routes.append((route_id, file_name))

# לולאה לכל Route ID ברשימה
for route_id, file_name in routes:
    query = f"""
    SELECT s.shape_pt_lat, s.shape_pt_lon, CAST(s.shape_pt_sequence AS INTEGER) AS seq_num
    FROM public.shapes s
    JOIN public.open_maps rs ON rs.shape_id = s.shape_id
    WHERE rs.route_id = '{route_id}'
    ORDER BY seq_num;
    """

    # ביצוע השאילתא
    cursor.execute(query)
    points = cursor.fetchall()

    # הסרת כפילויות – אם אותה נקודה חוזרת פעמיים ברצף, נשמיט אותה
    clean_points = []
    last_point = None

    for lat, lon, _ in points:  # הפעם first = lat, second = lon
        current_point = [lat, lon]  # הפכנו את הסדר
        if current_point != last_point:
            clean_points.append(current_point)
        last_point = current_point

    # יצירת GeoJSON תקני
    geojson_output = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": clean_points  # עכשיו זה בפורמט [LAT, LON]
                },
                "properties": {
                    "route_id": route_id
                }
            }
        ]
    }

    # נתיב הקובץ לפי השם שנמצא בעמודה B בקובץ ה-CSV
    file_path = f"C:/Users/Costa/Desktop/GEOJSON/{file_name}.geojson"

    # שמירת הקובץ
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(geojson_output, f, ensure_ascii=False, indent=4)

    print(f"✅ קובץ {file_name}.geojson נשמר בהצלחה!")

# סגירת החיבור למסד הנתונים
cursor.close()
conn.close()

print("🎉 כל הקבצים נוצרו בהצלחה!")
