import os
import threading
from flask import Flask
import telebot

# =====================================================================
# 1. CẤU HÌNH TOKEN VÀ KHỞI TẠO BOT
# =====================================================================
# Sử dụng Token mới bạn vừa tạo từ @BotFather
TOKEN = "8908704004:AAGop1grfkEW3CUykNoRvw46Is1DctTQgno"
bot = telebot.TeleBot(TOKEN)

# Khởi tạo Flask Web Server để đáp ứng cơ chế "Keep Alive" của Render (Tránh bot bị ngủ đông)
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

        # [QUAN TRỌNG] Ghi nhận lại ID và Username ra hệ thống Logs của Render để bạn xem
        print(f"\n[🔥 NGƯỜI DÙNG MỚI TRUY CẬP]")
        print(f" -> Telegram ID: {user_id}")
        print(f" -> Username   : @{username}")
        print(f" -> Tên đầy đủ : {full_name}")
        print(f"----------------------------------------")

        # Gửi tin nhắn phản hồi đầu tiên cho người dùng
        bot.send_message(
            chat_id=message.chat.id, 
            text=f"👋 Chào mừng {full_name} đến với hệ thống!\n\n⏳ File thông báo của bạn đang được xử lý và tải lên ngay lập tức. Vui lòng đợi trong giây lát..."
        )

        # Định nghĩa tên file APK nằm cùng thư mục gốc của code
        file_name = "Thongbaoupto.apk"

        # Kiểm tra xem file có thực sự tồn tại trên server (Render) trước khi gửi hay không
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
    """Hàm chạy cơ chế Long Polling của Telegram Bot dưới dạng luồng phụ (Thread)"""
    print("-> Đang khởi động cơ chế Telegram Bot Polling...")
    bot.remove_webhook()
    # infinity_polling giúp bot tự động kết nối lại nếu gặp sự cố mạng đột ngột
    bot.infinity_polling(timeout=10, long_polling_timeout=5)


if __name__ == "__main__":
    # 1. Chạy cơ chế đọc lệnh Telegram ở một luồng độc lập, tránh làm nghẽn Flask Web Server
    bot_thread = threading.Thread(target=run_bot_polling, daemon=True)
    bot_thread.start()

    # 2. Khởi chạy Flask Web Server để lắng nghe Port được Render cấp phát động
    print("-> Đang khởi động Flask Web Server...")
    bind_port = int(os.environ.get("PORT", 5000))
    # Chạy host 0.0.0.0 để môi trường ngoài (Render) có thể ping tới
    app.run(host='0.0.0.0', port=bind_port)