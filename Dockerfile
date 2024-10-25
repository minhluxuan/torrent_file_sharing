# Dockerfile
FROM node:18

# Đặt thư mục làm việc
WORKDIR /app

# Sao chép package.json và package-lock.json
COPY package*.json ./

# Cài đặt dependencies
# RUN npm install

# Sao chép mã nguồn vào container
COPY . .

# Mở cổng ứng dụng
EXPOSE 3000

# Khởi động ứng dụng
CMD ["node", "dist/main.js"]
