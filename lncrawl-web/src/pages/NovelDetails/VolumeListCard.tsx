import { type Novel, type ReadHistory, type Volume } from '@/types';
import { stringifyError } from '@/utils/errors';
import { Card, Collapse, message, Typography } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { VolumeDetailsCard } from './VolumeDetailsCard';

export const VolumeListCard: React.FC<{
  novel: Novel;
}> = ({ novel }) => {
  const [messageApi, contextHolder] = message.useMessage();
  const [volumes, setVolumes] = useState<Volume[]>([]);
  const [history, setHistory] = useState<ReadHistory>({});

  useEffect(() => {
    const fetchVolumes = async (id: string) => {
      setVolumes([]);
      try {
        const { data: volumes } = await axios.get<Volume[]>(
          `/api/novel/${id}/volumes`
        );
        setVolumes(volumes);
      } catch (err) {
        messageApi.error(stringifyError(err));
      }
    };

    const fetchReadHistory = async (id: string) => {
      setHistory({});
      try {
        const { data: hisotry } = await axios.get<ReadHistory>(
          `/api/read-history/by-novel`,
          {
            params: {
              novel_id: id,
            },
          }
        );
        setHistory(hisotry);
      } catch (err) {
        messageApi.error(stringifyError(err));
      }
    };

    fetchVolumes(novel.id);
    fetchReadHistory(novel.id);
  }, [novel.id, messageApi]);

  return (
    <Card
      title="Table of Contents"
      styles={{
        body: { padding: 10 },
        title: { fontSize: 22 },
      }}
    >
      {contextHolder}

      <Collapse
        accordion
        items={volumes.map((volume) => ({
          key: volume.id,
          label: volume.title,
          children: (
            <VolumeDetailsCard inner volume={volume} history={history} />
          ),
          extra: (
            <Typography.Text
              type="secondary"
              style={{ fontSize: '12px', whiteSpace: 'nowrap' }}
            >
              {Intl.NumberFormat('en').format(volume.chapter_count)} chapters
            </Typography.Text>
          ),
          styles: {
            body: { padding: 0 },
            header: { textTransform: 'capitalize' },
          },
        }))}
      />
    </Card>
  );
};
