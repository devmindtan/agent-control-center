# Agent Control Center

Trang web chỉ đọc để xem bộ cấu hình **dùng chung cho mọi agent** của OpenCode:
skills, workflow và quy tắc trong `~/.config/opencode`.

## Mở trang

### Chế độ live (khuyến nghị)

```bash
python3 serve.py
```

Server chỉ nghe `127.0.0.1:8765`, tự mở trình duyệt, và **quét lại cấu hình ở
mỗi lần tải trang** — không cần build. Sửa skill/quy tắc xong chỉ cần nhấn F5.

Cũng có thể bấm **Agent Control Center** trong app menu (launcher đã cài tại
`~/.local/share/applications/agent-control-center.desktop`).

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

8 skill mới cho phát triển ứng dụng: `ui-ux-pro-max`, `design-system`,
`ui-styling`, `supabase`, `supabase-postgres-best-practices`,
`react-native-best-practices`, `react-navigation`, `upgrading-react-native`.

Gồm 4 tab: **Tổng quan** (số liệu, nguồn skill, tình trạng), **Skills** (tìm,
lọc theo phạm vi/nhóm, bấm để xem đường dẫn và nguồn), **Workflow** (chuỗi
`/plan → /check → /review → /commit`), **Quy tắc** (AGENTS.md, cấu hình và mục
lục để nhảy nhanh giữa các mục).

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
├── index.html   # UI + logic hiển thị (không dependency, không CDN)
├── serve.py     # server local, quét live mỗi lần tải trang
├── data.js      # snapshot cho bản tĩnh — đừng sửa tay
├── build.py     # quét cấu hình, sinh data.js
└── README.md
```

Yêu cầu: `python3`, trình duyệt bất kỳ. Font dùng font hệ thống nên chạy offline
hoàn toàn; server không gửi dữ liệu ra ngoài máy.
