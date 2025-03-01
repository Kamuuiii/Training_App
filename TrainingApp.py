#TrainingApp.py
import sqlite3
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import calendar
from kivy.clock import Clock
from datetime import datetime
from kivy.properties import StringProperty

#日本語フォントに対応
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path
resource_add_path('C:\Windows\Fonts')
LabelBase.register(DEFAULT_FONT, 'msgothic.ttc')

############################################################################################

#メインページ
class MainPage(Screen):
    def go_to_today_training(self):
        today_date = datetime.now().strftime("%Y/%m/%d")
        app = App.get_running_app()

        history_screen = app.root.get_screen('history')
        history_screen.set_date(today_date)

        addtraining_screen = app.root.get_screen('addtraining')
        addtraining_screen.set_date(today_date)

#カレンダーを表示するページ
class CalenderPage(Screen):
    pass

# データベース作成
def initialize_db():
    conn1 = sqlite3.connect('chest.db')
    c1 = conn1.cursor()
    c1.execute('''CREATE TABLE IF NOT EXISTS chest_exercises (name TEXT)''')
    c1.execute('SELECT COUNT(*) FROM chest_exercises')
    if c1.fetchone()[0] == 0:
        c1.execute('''INSERT INTO chest_exercises (name) VALUES ('ベンチプレス'), ('チェストプレス'), ('ペックフライ')''')
    conn1.commit()
    conn1.close()

    conn2 = sqlite3.connect('back.db')
    c2 = conn2.cursor()
    c2.execute('''CREATE TABLE IF NOT EXISTS back_exercises (name TEXT)''')
    c2.execute('SELECT COUNT(*) FROM back_exercises')
    if c2.fetchone()[0] == 0:
        c2.execute('''INSERT INTO back_exercises (name) VALUES ('チンニング(懸垂)'), ('ラットプルダウン'), ('デッドリフト')''')
    conn2.commit()
    conn2.close()

    conn3 = sqlite3.connect('leg.db')
    c3 = conn3.cursor()
    c3.execute('''CREATE TABLE IF NOT EXISTS leg_exercises (name TEXT)''')
    c3.execute('SELECT COUNT(*) FROM leg_exercises')
    if c3.fetchone()[0] == 0:
        c3.execute('''INSERT INTO leg_exercises (name) VALUES ('スクワット'), ('レッグエクステンション'), ('レッグカール')''')
    conn3.commit()
    conn3.close()

    conn4 = sqlite3.connect('shoulder.db')
    c4 = conn4.cursor()
    c4.execute('''CREATE TABLE IF NOT EXISTS shoulder_exercises (name TEXT)''')
    c4.execute('SELECT COUNT(*) FROM shoulder_exercises')
    if c4.fetchone()[0] == 0:
        c4.execute('''INSERT INTO shoulder_exercises (name) VALUES ('ショルダープレス'), ('サイドレイズ')''')
    conn4.commit()
    conn4.close()

    conn5 = sqlite3.connect('arm.db')
    c5 = conn5.cursor()
    c5.execute('''CREATE TABLE IF NOT EXISTS arm_exercises (name TEXT)''')
    c5.execute('SELECT COUNT(*) FROM arm_exercises')
    if c5.fetchone()[0] == 0:
        c5.execute('''INSERT INTO arm_exercises (name) VALUES ('アームカール'), ('バーベルカール'), ('フレンチプレス')''')
    conn5.commit()
    conn5.close()

    conn6 = sqlite3.connect('others.db')
    c6 = conn6.cursor()
    c6.execute('''CREATE TABLE IF NOT EXISTS others_exercises (name TEXT)''')
    c6.execute('SELECT COUNT(*) FROM others_exercises')
    if c6.fetchone()[0] == 0:
        c6.execute('''INSERT INTO others_exercises (name) VALUES ('プランク')''')
    conn6.commit()
    conn6.close()

    conn7 = sqlite3.connect('records.db')
    c7 = conn7.cursor()
    c7.execute('''CREATE TABLE IF NOT EXISTS records (
                    date TEXT, 
                    body_part TEXT, 
                    exercise TEXT, 
                    weight REAL, 
                    set_count INTEGER, 
                    rep_count INTEGER)''')
    conn7.commit()
    conn7.close()

# 種目名の管理
class ExerciseName(Screen):
    db_name = StringProperty('')
    table_name = StringProperty('')

    def __init__(self, title, db_name, table_name, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.db_name = db_name
        self.table_name = table_name
        self.display_all = False

        self.ids.title_label.text = self.title
        self.update_data_view()

    def update_data_view(self):
        data = self.get_data_from_db()
        self.ids.data_layout.clear_widgets()
        data_to_display = data if self.display_all else data[:]
        for item in data_to_display:
            btn = Button(text=item, size_hint_y=None, height=100)
            btn.bind(on_release=self.open_addtraining)
            self.ids.data_layout.add_widget(btn)

    def get_data_from_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM {self.table_name}")
        data = [name[0] for name in cursor.fetchall()]
        conn.close()
        return data

    def open_addtraining(self, button):
        addtraining_screen = self.manager.get_screen('addtraining')
        addtraining_screen.exercise_name = button.text
        self.manager.transition.direction = 'left'
        self.manager.current = 'addtraining'
    
    def delete_exercise(self):
        delete_screen = self.manager.get_screen('delete')
        delete_screen.previous_screen = self.name
        delete_screen.previous_screen_db_name = self.db_name
        delete_screen.previous_screen_table_name = self.table_name
        self.manager.transition.direction = 'left'
        self.manager.current = 'delete'

# 種目の追加
class AddExercisePage(Screen):
    previous_screen_db_name = StringProperty('')
    previous_screen_table_name = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.previous_screen = None

    def on_pre_enter(self, *args):
        self.ids.exercise_name.text = ''

    def add_exercise(self, exercise_name):
        if exercise_name:
            conn = sqlite3.connect(self.previous_screen_db_name)
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {self.previous_screen_table_name} (name) VALUES (?)", (exercise_name,))
            conn.commit()
            conn.close()
            self.manager.get_screen(self.previous_screen).update_data_view()

# 種目の削除
class DeleteExercisePage(Screen):
    previous_screen_db_name = StringProperty('')
    previous_screen_table_name = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.previous_screen = None

    def on_pre_enter(self, *args):
        self.update_data_view()

    def update_data_view(self):
        data = self.get_data_from_db()
        self.ids.data_layout.clear_widgets()
        for item in data:
            btn = Button(text=item, size_hint_y=None, height=100)
            btn.bind(on_release=self.confirm_delete)
            self.ids.data_layout.add_widget(btn)

    def get_data_from_db(self):
        conn = sqlite3.connect(self.previous_screen_db_name)
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM {self.previous_screen_table_name}")
        data = [name[0] for name in cursor.fetchall()]
        conn.close()
        return data

    def confirm_delete(self, button):
        exercise_name = button.text
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=f'{exercise_name}を削除しますか？'))

        buttons = BoxLayout(size_hint_y=None, height=50)
        yes_button = Button(text='はい')
        no_button = Button(text='いいえ')
        buttons.add_widget(yes_button)
        buttons.add_widget(no_button)
        content.add_widget(buttons)

        popup = Popup(title='', content=content, size_hint=(0.8, 0.4))
        
        yes_button.bind(on_release=lambda x: self.delete_exercise(popup, exercise_name))
        no_button.bind(on_release=popup.dismiss)
        
        popup.open()

    def delete_exercise(self, popup, exercise_name):
        conn = sqlite3.connect(self.previous_screen_db_name)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {self.previous_screen_table_name} WHERE name=?", (exercise_name,))
        conn.commit()
        conn.close()
        popup.dismiss()
        self.update_data_view()
        self.manager.get_screen(self.previous_screen).update_data_view()
        self.manager.transition.direction = 'right'
        self.manager.current = self.previous_screen

# 部位の選択
class SelectExercisePage(Screen):
    pass

# 履歴を保存するデータベース
class Record:
    def __init__(self, date, body_part, exercise, weight, set_count, rep_count):
        self.date = date
        self.body_part = body_part
        self.exercise = exercise
        self.weight = weight
        self.set_count = set_count
        self.rep_count = rep_count

    def save_to_db(self):
        conn = sqlite3.connect('records.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS records (
                        date TEXT, 
                        body_part TEXT, 
                        exercise TEXT, 
                        weight REAL, 
                        set_count INTEGER, 
                        rep_count INTEGER)''')
        c.execute('''INSERT INTO records (date, body_part, exercise, weight, set_count, rep_count) 
                    VALUES (?, ?, ?, ?, ?, ?)''',
                  (self.date, self.body_part, self.exercise, self.weight, self.set_count, self.rep_count))
        conn.commit()
        conn.close()

    @staticmethod
    def get_records_by_date(date):
        conn = sqlite3.connect('records.db')
        c = conn.cursor()
        c.execute('SELECT date, body_part, exercise, weight, set_count, rep_count FROM records WHERE date=? ORDER BY exercise, set_count', (date,))
        records = c.fetchall()
        conn.close()
        return records

    @staticmethod
    def get_records_by_date_and_exercise(date, exercise):
        conn = sqlite3.connect('records.db')
        c = conn.cursor()
        c.execute('SELECT set_count, weight, rep_count FROM records WHERE date=? AND exercise=? ORDER BY set_count', (date, exercise))
        records = c.fetchall()
        conn.close()
        return records

# トレーニング記録を追加する画面
class AddTrainingPage(Screen):
    exercise_name = StringProperty('')
    body_part = StringProperty('')
    date = StringProperty('')

    def set_date(self, date):
        self.date = datetime.strptime(date, "%Y/%m/%d").strftime("%Y/%m/%d")


    def on_pre_enter(self, *args):
        # ここで self.date が設定されていない場合は、現在の日付を使用
        if not self.date:
            self.date = datetime.now().strftime("%Y/%m/%d")

        self.ids.addtraining_label.text = f"{self.exercise_name}"
        self.ids.date_label.text = f"{self.date}"
        self.ids.sets_layout.clear_widgets()
        self.records = []

        existing_records = Record.get_records_by_date_and_exercise(self.date, self.exercise_name)
        if existing_records:
            for set_number, weight, rep_count in existing_records:
                self.add_existing_set(set_number, weight, rep_count)
            self.set_counter = len(existing_records) + 1
        else:
            self.set_counter = 1
            self.add_set()

    def add_set(self):
        set_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        set_label = Label(text=f"{self.set_counter}セット目", size_hint_y=None, height=50)
        weight_input = TextInput(hint_text='重さ (kg)', multiline=False, size_hint_y=None, height=50)
        rep_input = TextInput(hint_text='回数', multiline=False, size_hint_y=None, height=50)
        remove_button = Button(text='削除', size_hint_y=None, height=50)

        set_layout.add_widget(set_label)
        set_layout.add_widget(weight_input)
        set_layout.add_widget(rep_input)
        set_layout.add_widget(remove_button)
        self.ids.sets_layout.add_widget(set_layout)

        remove_button.bind(on_release=lambda x: self.remove_set(set_layout))

        self.records.append((self.set_counter, weight_input, rep_input, set_layout))
        self.set_counter += 1

    def add_existing_set(self, set_number, weight, rep_count):
        set_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        set_label = Label(text=f"{set_number}セット目", size_hint_y=None, height=50)
        weight_input = TextInput(text=str(weight), multiline=False, size_hint_y=None, height=50)
        rep_input = TextInput(text=str(rep_count), multiline=False, size_hint_y=None, height=50)
        remove_button = Button(text='削除', size_hint_y=None, height=50)

        set_layout.add_widget(set_label)
        set_layout.add_widget(weight_input)
        set_layout.add_widget(rep_input)
        set_layout.add_widget(remove_button)
        self.ids.sets_layout.add_widget(set_layout)

        remove_button.bind(on_release=lambda x: self.remove_set(set_layout))

        self.records.append((set_number, weight_input, rep_input, set_layout))

    def remove_set(self, set_layout):
        self.ids.sets_layout.remove_widget(set_layout)
        self.records = [record for record in self.records if record[3] != set_layout]
        self.update_set_numbers()

    def update_set_numbers(self):
        for i, (set_number, weight_input, rep_input, set_layout) in enumerate(self.records, start=1):
            set_label = set_layout.children[3]
            set_label.text = f"{i}セット目"
            record_index = self.records.index((set_number, weight_input, rep_input, set_layout))
            self.records[record_index] = (i, weight_input, rep_input, set_layout)
        self.set_counter = len(self.records) + 1

    def save_record(self):
        for set_number, weight_input, rep_input, set_layout in self.records:
            if not weight_input.text or not rep_input.text:
                self.ids.error_message.text = "重さと回数を入力してください。"
                return
        self.ids.error_message.text = ""

        conn = sqlite3.connect('records.db')
        c = conn.cursor()
        c.execute('''DELETE FROM records WHERE date=? AND body_part=? AND exercise=?''',
                  (self.date, self.body_part, self.exercise_name))
        conn.commit()
        conn.close()

        for set_number, weight_input, rep_input, set_layout in self.records:
            weight = float(weight_input.text)
            rep_count = int(rep_input.text)
            record = Record(self.date, self.body_part, self.exercise_name, weight, set_number, rep_count)
            record.save_to_db()

        self.manager.transition.direction = 'right'
        self.manager.current = 'history'

# 履歴を表示する画面
class HistoryPage(Screen):
    date = StringProperty('')

    def set_date(self, date):
        self.date = datetime.strptime(date, "%Y/%m/%d").strftime("%Y/%m/%d")
        self.ids.date_label.text = f"{self.date}"

    def on_pre_enter(self, *args):
        self.update_history()

    def update_history(self):
        self.ids.history_layout.clear_widgets()
        records = Record.get_records_by_date(self.date)
        if records:
            current_exercise = None
            for date, body_part, exercise, weight, set_count, rep_count in records:
                if exercise != current_exercise:
                    current_exercise = exercise
                    self.ids.history_layout.add_widget(Label(text=f"{exercise}", size_hint_y=None, height=50))
                self.ids.history_layout.add_widget(Label(
                    text=f"{set_count}: {weight}kg {rep_count}回",
                    size_hint_y=None,
                    height=50
                ))
        else:
            self.ids.history_layout.add_widget(Label(text="トレーニング記録がありません", size_hint_y=None, height=50))

# カレンダーの表示制御
class CalendarWidget(GridLayout):
    month_label_text = StringProperty()
    month_names_jp = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 7  # 7 columns for the days of the week
        self.days_of_week = ['日', '月', '火', '水', '木', '金', '土']
        self.now = datetime.now()
        self.year = self.now.year
        self.month = self.now.month
        self.update_calendar()

    def update_calendar(self):
        self.clear_widgets()
        font_size = '20sp'

        for day in self.days_of_week:
            self.add_widget(Label(text=day, font_size=font_size))

        first_day_of_month, number_of_days = calendar.monthrange(self.year, self.month)
        start_position = (first_day_of_month + 1) % 7

        for _ in range(start_position):
            self.add_widget(Label(text='', font_size=font_size))

        for day in range(1, number_of_days + 1):
            btn = Button(text=str(day), font_size=font_size)
            btn.bind(on_press=self.on_date_press)
            self.add_widget(btn)

        self.month_label_text = f'{self.year}年 {self.month_names_jp[self.month - 1]}'

    def on_date_press(self, instance):
        selected_date = f"{self.year}/{self.month:02d}/{int(instance.text):02d}"

        try:
            app = App.get_running_app()
            
            history_screen = app.root.get_screen('history')
            history_screen.set_date(selected_date)
            app.root.transition.direction = 'left'
            app.root.current = 'history'

            addtraining_screen = app.root.get_screen('addtraining')
            addtraining_screen.set_date(selected_date)

        except Exception as e:
            print(f"Error in on_date_press: {e}")

    def previous_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.update_calendar()

    def next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.update_calendar()

# アプリケーションの構築
class TrainingApp(App):
    def build(self):
        initialize_db()
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(MainPage(name='main'))
        sm.add_widget(SelectExercisePage(name='bodypart'))
        sm.add_widget(AddExercisePage(name='addexercise'))
        sm.add_widget(DeleteExercisePage(name='delete'))
        sm.add_widget(CalenderPage(name='calender'))
        sm.add_widget(AddTrainingPage(name='addtraining'))
        sm.add_widget(HistoryPage(name='history'))

        databases = [
            ('chest', '胸', 'chest.db', 'chest_exercises'),
            ('back', '背中', 'back.db', 'back_exercises'),
            ('leg', '脚', 'leg.db', 'leg_exercises'),
            ('shoulder', '肩', 'shoulder.db', 'shoulder_exercises'),
            ('arm', '腕', 'arm.db', 'arm_exercises'),
            ('others', 'その他', 'others.db', 'others_exercises')
        ]

        for name, title, db_name, table_name in databases:
            screen = ExerciseName(title=title, db_name=db_name, table_name=table_name, name=name)
            sm.add_widget(screen)


        return sm
    
if __name__ == '__main__':
    TrainingApp().run()