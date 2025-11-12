import { type Job, type ReadHistory, type Volume } from '@/types';
import { stringifyError } from '@/utils/errors';
import { DownloadOutlined } from '@ant-design/icons';
import { Button, Card, Collapse, message, Space, Typography } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { VolumeDetailsCard } from './VolumeDetailsCard';

export const VolumeListCard: React.FC<{
  novelId: string;
  inner?: boolean;
}> = ({ novelId, inner }) => {
  const navigate = useNavigate();
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

    fetchVolumes(novelId);
    fetchReadHistory(novelId);
  }, [novelId, messageApi]);

  const createVolumeJob = async (e: React.MouseEvent, id: string) => {
    try {
      e.stopPropagation();
      e.preventDefault();
      const result = await axios.post<Job>(`/api/job/create/fetch-volumes`, {
        volumes: [id],
      });
      navigate(`/job/${result.data.id}`);
    } catch (err) {
      messageApi.error(stringifyError(err));
    }
  };

  return (
    <Card
      type={inner ? 'inner' : undefined}
      title={!inner && 'Table of Contents'}
      variant={inner ? 'borderless' : 'outlined'}
      style={{ borderRadius: inner ? 0 : undefined }}
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
            <Space size="small">
              <Typography.Text
                type="secondary"
                style={{ fontSize: '12px', whiteSpace: 'nowrap' }}
              >
                {Intl.NumberFormat('en').format(volume.chapter_count)} chapters
              </Typography.Text>

              <Button
                size="small"
                shape="round"
                type="primary"
                style={{ width: 75 }}
                icon={<DownloadOutlined />}
                onClick={(e) => createVolumeJob(e, volume.id)}
              >
                Get
              </Button>
            </Space>
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
