# Agent Control Center

Trang web tĩnh, chỉ đọc, để xem bộ cấu hình **dùng chung cho mọi agent** của
OpenCode: skills, workflow và quy tắc trong `~/.config/opencode`.

Mở bằng trình duyệt — không cần server, không cần mạng:

```bash
xdg-open index.html
```

## Đang hiển thị gì

| Mục | Số | Nguồn |
| --- | --- | --- |
| Skill toàn cục | 46 | `~/.config/opencode/skills/` (44 symlink + 2 bản copy) |
| Skill built-in | 3 | `opencode`, `report`, `browser` |
| Skill Claude synced | 4 | `~/.claude/skills/synced/` |
| Lệnh workflow | 4 | `~/.config/opencode/commands/` |
| Quy tắc | 1 | `~/.config/opencode/AGENTS.md` |
| Agent / MCP riêng | 0 | — |

Gồm 4 tab: **Tổng quan** (số liệu, nguồn skill, tình trạng), **Skills** (tìm,
lọc theo phạm vi/nhóm, bấm để xem đường dẫn và nguồn), **Workflow** (chuỗi
`/plan → /check → /review → /commit`), **Quy tắc** (AGENTS.md và cấu hình).

## Cập nhật số liệu

Trang không sửa gì. Sau khi thay đổi cấu hình, chạy lại script quét:

```bash
python3 build.py
```

Script đọc trực tiếp các file trong `~/.config/opencode` (và gọi
`opencode api get /api/skill` nếu server đang chạy), rồi ghi lại `data.js`.

## Muốn agent sửa gì, cứ nhắn

Ví dụ:

- “Thêm skill `foo` vào global, lấy từ `~/Documents/code/.../foo`.”
- “Sửa mô tả skill `playwright` cho ngắn hơn.”
- “Đổi `/plan`: luôn đọc `AGENTS.md` của dự án trước.”
- “Gỡ skill không dùng, chạy lại `link-skills.sh` rồi build lại trang.”
- “Thêm mục quy tắc về cách viết commit vào `AGENTS.md`.”

Agent sửa file nguồn trong `~/.config/opencode`, chạy `python3 build.py`, và
trang sẽ phản ánh thay đổi ở lần mở tiếp theo.

## Cấu trúc

```
agent-control-center/
├── index.html   # UI + logic hiển thị (không dependency, không CDN)
├── data.js      # dữ liệu sinh tự động — đừng sửa tay
├── build.py     # quét cấu hình, sinh data.js
└── README.md
```

Yêu cầu: `python3` để build, trình duyệt bất kỳ để xem. Font dùng font hệ
thống nên chạy offline hoàn toàn.
