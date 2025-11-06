#!/bin/bash
# Script setup tự động cho n8n workflow
# Chạy script này trên server để setup môi trường

set -e

echo "🚀 Bắt đầu setup n8n script environment..."

# Kiểm tra đang ở đâu
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "📁 Script directory: $SCRIPT_DIR"

# Tạo thư mục scripts trong n8n-data
N8N_DATA_DIR="$HOME/n8n-data"
SCRIPTS_DIR="$N8N_DATA_DIR/scripts"

echo "📦 Tạo thư mục scripts..."
mkdir -p "$SCRIPTS_DIR"

# Copy script vào thư mục scripts
if [ -f "$SCRIPT_DIR/auto_extractor_json.py" ]; then
    echo "📋 Copy auto_extractor_json.py..."
    cp "$SCRIPT_DIR/auto_extractor_json.py" "$SCRIPTS_DIR/"
    chmod +x "$SCRIPTS_DIR/auto_extractor_json.py"
    echo "✅ Đã copy script"
else
    echo "⚠️  Không tìm thấy auto_extractor_json.py trong $SCRIPT_DIR"
    echo "   Vui lòng đảm bảo file tồn tại hoặc copy thủ công"
fi

# Kiểm tra docker-compose.yml
COMPOSE_FILE="$N8N_DATA_DIR/docker-compose.yml"
if [ -f "$COMPOSE_FILE" ]; then
    echo "🔍 Kiểm tra docker-compose.yml..."
    
    # Kiểm tra xem đã có volume mount chưa
    if grep -q "/home/node/scripts" "$COMPOSE_FILE"; then
        echo "✅ Volume mount đã được cấu hình"
    else
        echo "⚠️  Chưa có volume mount cho scripts"
        echo "   Cần thêm dòng sau vào volumes section:"
        echo "   - ./scripts:/home/node/scripts"
        echo ""
        echo "   Bạn có muốn tự động thêm không? (y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            # Backup file
            cp "$COMPOSE_FILE" "$COMPOSE_FILE.backup"
            
            # Thêm volume mount (tìm dòng volumes và thêm sau đó)
            if grep -q "n8n-local-files:/home/node/.n8n" "$COMPOSE_FILE"; then
                sed -i '/n8n-local-files:\/home\/node\/\.n8n/a\      - ./scripts:/home/node/scripts' "$COMPOSE_FILE"
                echo "✅ Đã thêm volume mount"
            else
                echo "❌ Không tìm thấy volumes section, cần thêm thủ công"
            fi
        fi
    fi
else
    echo "⚠️  Không tìm thấy docker-compose.yml tại $COMPOSE_FILE"
fi

# Hướng dẫn cài dependencies
echo ""
echo "📚 Bước tiếp theo:"
echo "1. Restart n8n container:"
echo "   cd $N8N_DATA_DIR && docker compose restart"
echo ""
echo "2. Vào container và cài Python dependencies:"
echo "   docker exec -it n8n-data-n8n-1 sh"
echo "   apk add python3 py3-pip"
echo "   pip3 install scrapetube youtube-transcript-api"
echo ""
echo "3. Test script:"
echo "   docker exec -it n8n-data-n8n-1 sh -c 'cd /home/node/scripts && python3 auto_extractor_json.py --output-json'"
echo ""
echo "✅ Setup hoàn tất!"

