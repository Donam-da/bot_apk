import os
import threading
from datetime import datetime
from flask import Flask
import telebot

# =====================================================================
# 1. CẤU HÌNH TOKEN VÀ KHỞI TẠO BOT
# =====================================================================
# Sử dụng Token được lấy từ Environment Variable trên Render
TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Danh sách lưu trữ thông tin người dùng đã truy cập
users_list = []

# Khởi tạo Flask Web Server để phục vụ cơ chế "Keep Alive" tránh bot bị ngủ đông
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot đang chạy ngon lành 24/7 trên Render!"


# =====================================================================
# 2. XỬ LÝ SỰ KIỆN KHI NGƯỜI DÙNG ẤN /START
# =====================================================================
@bot.message_handler(commands=['start'])
def handle_start_command(message):
    try:
        # Lấy thông tin tài khoản chi tiết của người tương tác
        user_id = message.from_user.id
        username = message.from_user.username if message.from_user.username else "Không có"
        first_name = message.from_user.first_name if message.from_user.first_name else ""
        last_name = message.from_user.last_name if message.from_user.last_name else ""
        full_name = f"{first_name} {last_name}".strip()

        # Ghi nhận lại ID và Username ra hệ thống Logs của Render
        print(f"\n[🔥 NGƯỜI DÙNG MỚI TRUY CẬP]")
        print(f" -> Telegram ID: {user_id}")
        print(f" -> Username   : @{username}")
        print(f" -> Tên đầy đủ : {full_name}")
        print(f"----------------------------------------")

        # Lưu thông tin người dùng vào danh sách
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Kiểm tra xem người dùng đã tồn tại trong danh sách chưa
        existing_user = next((u for u in users_list if u['id'] == user_id), None)
        
        if existing_user:
            # Cập nhật thông tin người dùng đã tồn tại
            existing_user['last_interaction'] = current_time
            existing_user['interaction_count'] += 1
        else:
            # Thêm người dùng mới
            user_info = {
                'id': user_id,
                'username': username,
                'full_name': full_name,
                'last_interaction': current_time,
                'interaction_count': 1
            }
            users_list.append(user_info)

        # Kiểm tra xem có phải admin không
        if user_id == 6762189023:
            # Admin: Hiện tin nhắn chào admin và gửi file
            bot.send_message(message.chat.id, "👋 Chào admin, tôi là bot của bạn!")
        else:
            # User thường: Hiện tin nhắn chào mừng với thông tin liên hệ
            bot.send_message(
                message.chat.id,
                f"👋 Chào mừng {full_name} đến với hệ thống!\n\n💬 Ib @hfnam04 để mua bản app xịn."
            )

        # Định nghĩa tên file APK nằm cùng thư mục gốc của code
        file_name = "Apptbaouptolink.apk"

        # Kiểm tra xem file có thực sự tồn tại trên server trước khi gửi hay không
        if os.path.exists(file_name):
            print(f"[ℹ️ INFO] Đang gửi file APK cho ID: {user_id}")
            try:
                # Tiến hành đọc file dưới dạng nhị phân (rb) và gửi đi
                with open(file_name, 'rb') as file_to_send:
                    bot.send_document(
                        chat_id=message.chat.id,
                        document=file_to_send,
                        caption="📥 Đây là file cài đặt APK của bạn. Hãy tải xuống và cài đặt nhé!"
                    )
                print(f"[✅ THÀNH CÔNG] Đã tự động nhả file APK cho ID: {user_id}")
            except Exception as file_error:
                print(f"[❌ LỖI GỬI FILE] Không thể gửi file cho ID {user_id}: {str(file_error)}")
                bot.send_message(message.chat.id, f"❌ Không thể gửi file APK: {str(file_error)}")
        else:
            bot.send_message(message.chat.id, "❌ Hệ thống gặp sự cố: Không tìm thấy file cài đặt trên máy chủ.")
            print(f"[❌ THẤT BẠI] Lỗi: Không tìm thấy file '{file_name}' trong thư mục chạy bot.")

    except Exception as e:
        print(f"[❌ LỖI HỆ THỐNG] Đã có lỗi xảy ra trong quá trình xử lý: {str(e)}")


@bot.message_handler(commands=['stats'])
def handle_stats_command(message):
    try:
        # Kiểm tra quyền truy cập - chỉ ID 6762189023 mới được dùng lệnh này
        if message.from_user.id != 6762189023:
            bot.send_message(message.chat.id, "❌ Lệnh này không có trong bot.")
            return

        if not users_list:
            bot.send_message(message.chat.id, "📊 Chưa có người dùng nào truy cập bot.")
            return

        stats_text = "📊 **DANH SÁCH NGƯỜI DÙNG ĐÃ TRUY CẬP**\n\n"
        for idx, user in enumerate(users_list, 1):
            stats_text += f"{idx}. **ID:** {user['id']}\n"
            stats_text += f"   **Username:** @{user['username']}\n"
            stats_text += f"   **Tên:** {user['full_name']}\n"
            stats_text += f"   **Lần gần nhất:** {user['last_interaction']}\n"
            stats_text += f"   **Số lần tương tác:** {user['interaction_count']}\n\n"

        stats_text += f"👥 **Tổng số:** {len(users_list)} người dùng"
        bot.send_message(message.chat.id, stats_text, parse_mode='Markdown')

    except Exception as e:
        print(f"[❌ LỖI HỆ THỐNG] Đã có lỗi xảy ra khi xem stats: {str(e)}")


@bot.message_handler(func=lambda message: message.text == "📊 List")
def handle_list_button(message):
    try:
        # Kiểm tra quyền truy cập - chỉ ID 6762189023 mới được dùng nút này
        if message.from_user.id != 6762189023:
            bot.send_message(message.chat.id, "❌ Bạn không có quyền sử dụng tính năng này.")
            return

        if not users_list:
            bot.send_message(message.chat.id, "📊 Chưa có người dùng nào truy cập bot.")
            return

        stats_text = "📊 **DANH SÁCH NGƯỜI DÙNG ĐÃ TRUY CẬP**\n\n"
        for idx, user in enumerate(users_list, 1):
            stats_text += f"{idx}. **ID:** {user['id']}\n"
            stats_text += f"   **Username:** @{user['username']}\n"
            stats_text += f"   **Tên:** {user['full_name']}\n"
            stats_text += f"   **Lần gần nhất:** {user['last_interaction']}\n"
            stats_text += f"   **Số lần tương tác:** {user['interaction_count']}\n\n"

        stats_text += f"👥 **Tổng số:** {len(users_list)} người dùng"
        bot.send_message(message.chat.id, stats_text, parse_mode='Markdown')

    except Exception as e:
        print(f"[❌ LỖI HỆ THỐNG] Đã có lỗi xảy ra khi xem list: {str(e)}")


@bot.message_handler(commands=['menu'])
def handle_menu_command(message):
    try:
        # Kiểm tra quyền truy cập - chỉ ID 6762189023 mới được dùng lệnh này
        if message.from_user.id != 6762189023:
            bot.send_message(message.chat.id, "❌ Lệnh này không có trong bot.")
            return

        # Tạo keyboard với nút List
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        list_button = telebot.types.KeyboardButton("📊 List")
        markup.add(list_button)

        bot.send_message(message.chat.id, "📋 Menu admin đã được kích hoạt. Nhấn nút bên dưới để xem danh sách.", reply_markup=markup)

    except Exception as e:
        print(f"[❌ LỖI HỆ THỐNG] Đã có lỗi xảy ra khi kích hoạt menu: {str(e)}")


# =====================================================================
# 3. ĐIỀU KHIỂN CHẠY BOT VÀ WEB SERVER SONG SONG
# =====================================================================
def run_bot_polling():
    """Hàm chạy cơ chế Long Polling dưới dạng luồng phụ (Thread)"""
    print("-> Đang khởi động cơ chế Telegram Bot Polling...")
    try:
        bot.remove_webhook()
        # infinity_polling giúp bot duy trì và tự động kết nối lại nếu rớt mạng
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"[❌ LỖI THREAD BOT] Polling gặp sự cố: {str(e)}")


if __name__ == "__main__":
    print("========================================")
    print("-> Đang chuẩn bị kích hoạt hệ thống...")
    
    # 1. Chạy cơ chế đọc lệnh Telegram ở một luồng độc lập (Thread ngầm)
    bot_thread = threading.Thread(target=run_bot_polling, daemon=True)
    bot_thread.start()
    print("-> Luồng xử lý Telegram Bot đã được kích hoạt ngầm.")

    # 2. Khởi chạy Flask Web Server để Render có thể ping kiểm tra trạng thái port
    print("-> Đang khởi động Flask Web Server...")
    bind_port = int(os.environ.get("PORT", 5000))
    
    # Chạy host 0.0.0.0 và bật threaded=True để xử lý các luồng request song song ổn định
    app.run(host='0.0.0.0', port=bind_port, threaded=True, debug=False)