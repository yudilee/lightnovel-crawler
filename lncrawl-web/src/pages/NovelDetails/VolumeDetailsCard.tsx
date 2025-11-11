import { type Chapter, type ReadHistory, type Volume } from '@/types';
import { stringifyError } from '@/utils/errors';
import { formatDate } from '@/utils/time';
import { Card, Collapse, Descriptions, Grid, message } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ChapterDetailsCard } from './ChapterDetailsCard';

export const VolumeDetailsCard: React.FC<{
  volume: Volume;
  inner?: boolean;
  history?: ReadHistory;
}> = ({ volume, inner, history = {} }) => {
  const { lg } = Grid.useBreakpoint();
  const [messageApi, contextHolder] = message.useMessage();

  const [chapters, setChapters] = useState<Chapter[]>([]);

  useEffect(() => {
    const fetchChapters = async (id: string) => {
      try {
        const { data: chapters } = await axios.get<Chapter[]>(
          `/api/volume/${id}/chapters`
        );
        setChapters(chapters);
      } catch (err) {
        messageApi.error(stringifyError(err));
        setChapters([]);
      }
    };

    fetchChapters(volume.id);
  }, [volume.id, messageApi]);

  return (
    <Card
      type={inner ? 'inner' : undefined}
      title={inner ? undefined : volume.title}
      variant={inner ? 'borderless' : 'outlined'}
      styles={{
        body: {
          padding: 10,
        },
        title: {
          fontSize: 22,
          whiteSpace: 'wrap',
        },
      }}
    >
      {contextHolder}

      <Descriptions
        size="small"
        layout="horizontal"
        column={lg ? 3 : 1}
        bordered
        items={[
          {
            label: 'Serial',
            children: volume.serial,
          },
          {
            label: 'Chapters',
            children: volume.chapter_count ?? 0,
          },
          {
            label: 'Last Update',
            children: formatDate(volume.updated_at),
          },
        ]}
      />

      {chapters.length > 0 && (
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
              <Link to={`/read/${chapter.id}`}>Read</Link>
            ) : undefined,
          }))}
        />
      )}
    </Card>
  );
};
