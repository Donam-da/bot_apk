import os
import threading
import time
from flask import Flask
import telebot

# =====================================================================
# 1. CẤU HÌNH TOKEN VÀ KHỞI TẠO BOT
# =====================================================================
# Sử dụng Token được lấy từ Environment Variable trên Render
TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

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

        # Gửi tin nhắn phản hồi đầu tiên cho người dùng
        progress_message = bot.send_message(
            chat_id=message.chat.id, 
            text=f"👋 Chào mừng {full_name} đến với hệ thống!\n\n⏳ Đang xử lý file..."
        )

        # Hiển thị thanh tiến trình từ 0% đến 100%
        for progress in range(0, 101, 1):
            time.sleep(0.03)  # Đợi 0.03 giây giữa mỗi bước
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=progress_message.message_id,
                text=f"👋 Chào mừng {full_name} đến với hệ thống!\n\n⏳ Đang xử lý file... {progress}%"
            )

        # Định nghĩa tên file APK nằm cùng thư mục gốc của code
        file_name = "Apptbaouptolink.apk"

        # Kiểm tra xem file có thực sự tồn tại trên server trước khi gửi hay không
        if os.path.exists(file_name):
            # Tiến hành đọc file dưới dạng nhị phân (rb) và gửi đi
            with open(file_name, 'rb') as file_to_send:
                bot.send_document(
                    chat_id=message.chat.id, 
                    document=file_to_send, 
                    caption="📥 Đây là file cài đặt APK của bạn. Hãy tải xuống và cài đặt nhé!"
                )
            print(f"[✅ THÀNH CÔNG] Đã tự động nhả file APK cho ID: {user_id}")
        else:
            bot.send_message(message.chat.id, "❌ Hệ thống gặp sự cố: Không tìm thấy file cài đặt trên máy chủ.")
            print(f"[❌ THẤT BẠI] Lỗi: Không tìm thấy file '{file_name}' trong thư mục chạy bot.")

    except Exception as e:
        print(f"[❌ LỖI HỆ THỐNG] Đã có lỗi xảy ra trong quá trình xử lý: {str(e)}")


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