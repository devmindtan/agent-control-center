# Agent Control Center

Trang web chỉ đọc để xem bộ cấu hình **dùng chung cho mọi agent** của OpenCode:
skills, workflow và quy tắc trong `~/.config/opencode`.

Bốn tab: **Tổng quan** (số liệu, nguồn skill, tình trạng), **Skills** (tìm và lọc,
bấm để xem đường dẫn, nguồn), **Workflow** (`/plan → /check → /review → /commit`),
**Quy tắc** (AGENTS.md kèm mục lục).

Không dependency, không CDN, không gửi dữ liệu ra ngoài. Cần `python3` và một
trình duyệt.

## Cài đặt

```bash
git clone https://github.com/devmindtan/agent-control-center.git \
  ~/Documents/code/agent-control-center
cd ~/Documents/code/agent-control-center
./install.sh
```

Hoặc tải bản nén rồi cài:

```bash
curl -L https://github.com/devmindtan/agent-control-center/archive/refs/heads/main.tar.gz \
  | tar -xz -C ~/Documents/code
mv ~/Documents/code/agent-control-center-main ~/Documents/code/agent-control-center
cd ~/Documents/code/agent-control-center
./install.sh
```

`install.sh` chỉ tạo launcher cho user hiện tại tại
`~/.local/share/applications/agent-control-center.desktop`. Nó không đụng tới
skill hay cấu hình global: bộ skill dùng chung do
`~/.config/opencode/scripts/link-skills.sh` quản lý và không nằm trong repo này.

Repo: <https://github.com/devmindtan/agent-control-center> (public, nhánh `main`).
Nếu dùng SSH: `git clone git@github.com:devmindtan/agent-control-center.git`.

Cập nhật về sau:

```bash
cd ~/Documents/code/agent-control-center
git pull
./install.sh
```

Gỡ launcher (không xoá dữ liệu):

```bash
./install.sh --uninstall
```

## Mở trang

### Chế độ live (khuyến nghị)

```bash
python3 serve.py
```

Server chỉ nghe `127.0.0.1:8765`, tự mở trình duyệt, và **quét lại cấu hình ở
mỗi lần tải trang** — không cần build. Sửa skill/quy tắc xong chỉ cần nhấn F5.

Cũng có thể bấm **Agent Control Center** trong app menu.

Không muốn chạy server? Vẫn dùng được bản tĩnh:

```bash
python3 build.py        # cập nhật snapshot
xdg-open index.html
```

Trình duyệt không được phép đọc trực tiếp `~/.config/opencode` từ `file://`,
nên chế độ live cần server local nhỏ này. Cả hai chế độ đều đọc trực tiếp
`~/.config/opencode` (và gọi `opencode api get /api/skill` khi server đang chạy).

## Muốn agent sửa gì, cứ nhắn

Ví dụ:

- “Thêm skill `foo` vào global, lấy từ `~/Documents/code/.../foo`.”
- “Sửa mô tả skill `playwright` cho ngắn hơn.”
- “Đổi `/plan`: luôn đọc `AGENTS.md` của dự án trước.”
- “Gỡ skill không dùng, chạy lại `link-skills.sh`.”
- “Thêm mục quy tắc về cách viết commit vào `AGENTS.md`.”

Agent sửa file nguồn trong `~/.config/opencode`; ở chế độ live, tải lại trang là
thấy thay đổi ngay.

## Cấu trúc

```
agent-control-center/
├── index.html                  # UI + logic hiển thị
├── serve.py                    # server local, quét live mỗi lần tải trang
├── build.py                    # quét cấu hình, sinh data.js cho bản tĩnh
├── data.js                     # snapshot cho bản tĩnh — đừng sửa tay
├── install.sh                  # cài/gỡ launcher
├── agent-control-center.desktop # template launcher theo @DIR@
└── README.md
```

## Gỡ hoàn toàn (tuỳ chọn)

```bash
cd ~/Documents/code/agent-control-center
./install.sh --uninstall
cd ~
rm -rf ~/Documents/code/agent-control-center
```

Chỉ gỡ launcher và repo này; cấu hình trong `~/.config/opencode` giữ nguyên.
