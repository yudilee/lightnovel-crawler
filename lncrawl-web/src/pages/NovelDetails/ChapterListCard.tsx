import type { Chapter, ReadHistory } from '@/types';
import { RightCircleOutlined } from '@ant-design/icons';
import { Button, Collapse, theme } from 'antd';
import { useNavigate } from 'react-router-dom';
import { ChapterDetailsCard } from './ChapterDetailsCard';

export const ChapterListCard: React.FC<{
  chapters: Chapter[];
  history?: ReadHistory;
}> = ({ chapters, history = {} }) => {
  const navigate = useNavigate();
  const { token } = theme.useToken();

  return (
    <div style={{ marginTop: 10 }}>
      <Collapse
        ghost
        accordion
        size="small"
        items={chapters.map((chapter) => ({
          key: chapter.id,
          label: chapter.title,
          children: <ChapterDetailsCard inner chapter={chapter} />,
          styles: {
            body: { padding: 0 },
            header: {
              textTransform: 'capitalize',
              opacity: history[chapter.id] ? 0.5 : 1,
              borderBottom: `1px solid ${token.colorSplit}`,
            },
          },
          extra: (
            <Button
              size="small"
              shape="round"
              style={{ width: 75 }}
              icon={<RightCircleOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                e.preventDefault();
                navigate(`/read/${chapter.id}`);
              }}
            >
              Read
            </Button>
          ),
        }))}
      />
    </div>
  );
};
