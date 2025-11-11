import type { Chapter, Job, ReadHistory } from '@/types';
import { stringifyError } from '@/utils/errors';
import { DownloadOutlined, RightCircleOutlined } from '@ant-design/icons';
import { Button, Collapse, message, type ButtonProps } from 'antd';
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

  const stopPropagation =
    (cb: ButtonProps['onClick']): ButtonProps['onClick'] =>
    (e) => {
      e.stopPropagation();
      e.preventDefault();
      if (cb) cb(e);
    };

  return (
    <>
      {contextHolder}
      <Collapse
        accordion
        style={{ marginTop: 10 }}
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
              onClick={stopPropagation(() => navigate(`/read/${chapter.id}`))}
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
              onClick={stopPropagation(() => createChapterJob(chapter.id))}
            >
              Get
            </Button>
          ),
        }))}
      />
    </>
  );
};
