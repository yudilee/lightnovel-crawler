import { type Artifact, type Novel } from '@/types';
import { stringifyError } from '@/utils/errors';
import { Button, Flex, Grid, message, Result, Space, Spin } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { ArtifactListCard } from '../../components/ArtifactList/ArtifactListCard';
import { NovelDetailsCard } from './NovelDetailsCard';

export const NovelDetailsPage: React.FC<any> = () => {
  const { id } = useParams<{ id: string }>();

  const { lg } = Grid.useBreakpoint();
  const [messageApi, contextHolder] = message.useMessage();

  const [refreshId, setRefreshId] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  const [novel, setNovel] = useState<Novel>();
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);

  useEffect(() => {
    const fetchNovel = async (id: string) => {
      setError(undefined);
      try {
        const { data: novel } = await axios.get<Novel>(`/api/novel/${id}`);
        setNovel(novel);
      } catch (err: any) {
        setError(stringifyError(err));
      } finally {
        setLoading(false);
      }
    };

    const fetchArtifacts = async (id: string) => {
      try {
        const { data: artifacts } = await axios.get<Artifact[]>(
          `/api/novel/${id}/artifacts`
        );
        setArtifacts(artifacts);
      } catch (err) {
        messageApi.open({
          type: 'error',
          content: stringifyError(err, 'Failed to fetch artifacts'),
        });
      }
    };

    if (id) {
      fetchNovel(id);
      fetchArtifacts(id);
    }
  }, [id, refreshId, messageApi]);

  if (loading) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Spin size="large" style={{ marginTop: 100 }} />
      </Flex>
    );
  }

  if (error || !novel || !id) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Result
          status="error"
          title="Failed to load novel details"
          subTitle={error}
          extra={[
            <Button onClick={() => setRefreshId((v) => v + 1)}>Retry</Button>,
          ]}
        />
      </Flex>
    );
  }

  return (
    <Space direction="vertical" size={lg ? 'large' : 'small'}>
      {contextHolder}
      <NovelDetailsCard novel={novel} />
      <ArtifactListCard artifacts={artifacts} />
    </Space>
  );
};
