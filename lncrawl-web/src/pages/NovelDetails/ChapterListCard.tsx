import type { Chapter, Job, ReadHistory } from '@/types';
import { stringifyError } from '@/utils/errors';
import { DownloadOutlined, RightCircleOutlined } from '@ant-design/icons';
import { Button, Collapse, message } from 'antd';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { ChapterDetailsCard } from './ChapterDetailsCard';

export const ChapterListCard: React.FC<{
  chapters: Chapter[];
  history?: ReadHistory;
}> = ({ chapters, history = {} }) => {
  const navigate = useNavigate();
  const [messageApi, contextHolder] = message.useMessage();

  const createChapterJob = async (id: string) => {
    try {
      const result = await axios.post<Job>(`/api/job/create/fetch-chapters`, {
        chapters: [id],
      });
      navigate(`/job/${result.data.id}`);
    } catch (err) {
      messageApi.error(stringifyError(err));
    }
  };

  return (
    <div style={{ marginTop: 10 }}>
      {contextHolder}
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
              opacity: history[chapter.id] ? 0.5 : 1,
              textTransform: 'capitalize',
            },
          },
          extra: chapter.is_available ? (
            <Button
              size="small"
              shape="round"
              style={{ width: 75 }}
              icon={<RightCircleOutlined />}
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                navigate(`/read/${chapter.id}`);
              }}
            >
              Read
            </Button>
          ) : (
            <Button
              size="small"
              shape="round"
              type="primary"
              style={{ width: 75 }}
              icon={<DownloadOutlined />}
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                createChapterJob(chapter.id);
              }}
            >
              Get
            </Button>
          ),
        }))}
      />
    </div>
  );
};
