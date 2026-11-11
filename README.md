# Agent Control Center

Trang web chỉ đọc để xem bộ cấu hình **dùng chung cho mọi agent** của OpenCode:
skills, workflow và quy tắc trong `~/.config/opencode`.

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
skill hay cấu hình global.

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
nên chế độ live cần server local nhỏ này.

## Đang hiển thị gì

| Mục | Số | Nguồn |
| --- | --- | --- |
| Skill toàn cục | 54 | `~/.config/opencode/skills/` (51 symlink + 3 bản copy) |
| Skill built-in | 3 | `opencode`, `report`, `browser` |
| Skill Claude synced | 4 | `~/.claude/skills/synced/` |
| Tổng skill đăng ký | 61 | toàn cục + built-in + synced |
| Lệnh workflow | 4 | `~/.config/opencode/commands/` |
| Quy tắc | 1 | `~/.config/opencode/AGENTS.md` |
| Agent / MCP riêng | 0 | — |

8 skill cho phát triển ứng dụng: `ui-ux-pro-max`, `design-system`,
`ui-styling`, `supabase`, `supabase-postgres-best-practices`,
`react-native-best-practices`, `react-navigation`, `upgrading-react-native`.

Gồm 4 tab: **Tổng quan** (số liệu, nguồn skill, tình trạng), **Skills** (tìm,
lọc theo phạm vi/nhóm, bấm để xem đường dẫn và nguồn), **Workflow** (chuỗi
`/plan → /check → /review → /commit`), **Quy tắc** (AGENTS.md, cấu hình và mục
lục để nhảy nhanh giữa các mục).

## Trên máy này đã cài gì

| Đường dẫn | Nội dung |
| --- | --- |
| `~/Documents/code/agent-control-center` | repo này |
| `~/.local/share/applications/agent-control-center.desktop` | launcher app menu (do `install.sh` tạo) |
| `~/.config/opencode/skills/` | 54 skill toàn cục, gồm 8 skill mới |
| `~/.config/opencode/scripts/link-skills.sh` | thêm 3 nguồn repo và bản vá `ui-ux-pro-max` |
| `~/.config/opencode/AGENTS.md` | thêm định tuyến skill cho UI/UX, backend, mobile |
| `~/.config/opencode/README-skills.md` | bảng nguồn và điều kiện skill |
| `~/.config/opencode/README-workflow.md` | thêm mục Backend và Mobile |
| `~/Documents/code/agent-skill-repos/` | 3 repo clone shallow: ui-ux-pro-max, supabase, callstack |

Repo dashboard **không cài skill**. Nó chỉ đọc cấu hình đang có; muốn dựng lại bộ
skill trên máy khác thì clone các repo nguồn rồi chạy
`~/.config/opencode/scripts/link-skills.sh` (file này thuộc cấu hình global,
không nằm trong repo dashboard).

## Cập nhật dữ liệu

- **Live:** mở bằng `serve.py`, dữ liệu được quét lại mỗi lần tải trang.
- **Tĩnh:** chạy `python3 build.py` để ghi lại `data.js` từ cấu hình hiện tại.

Cả hai đều đọc trực tiếp `~/.config/opencode` (và gọi
`opencode api get /api/skill` nếu server đang chạy).

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
├── agent-control-center.desktop# template launcher
└── README.md
```

## Gỡ hoàn toàn (tuỳ chọn)

```bash
cd ~/Documents/code/agent-control-center
./install.sh --uninstall
cd ~
rm -rf ~/Documents/code/agent-control-center
```

8 skill mới và 3 repo nguồn là thay đổi riêng trong `~/.config/opencode` /
`~/Documents/code/agent-skill-repos`; chỉ xoá nếu bạn thật sự không dùng nữa,
và nhớ chạy lại `link-skills.sh` sau khi sửa danh sách.
