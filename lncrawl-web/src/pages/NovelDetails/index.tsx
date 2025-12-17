import { ErrorState } from '@/components/Loading/ErrorState';
import { LoadingState } from '@/components/Loading/LoadingState';
import { type Artifact, type Novel } from '@/types';
import { stringifyError } from '@/utils/errors';
import { Grid, message, Space } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { ArtifactListCard } from '../../components/ArtifactList/ArtifactListCard';
import { NovelDetailsCard } from './NovelDetailsCard';
import { VolumeListCard } from './VolumeListCard';

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

    if (id) {
      fetchNovel(id);
    }
  }, [id, refreshId, messageApi]);

  useEffect(() => {
    const fetchArtifacts = async (id: string) => {
      try {
        const { data: artifacts } = await axios.get<Artifact[]>(
          `/api/novel/${id}/artifacts`
        );
        setArtifacts(artifacts);
      } catch (err) {
        messageApi.error(stringifyError(err));
      }
    };

    setArtifacts([]);
    if (novel?.id) {
      fetchArtifacts(novel?.id);
    }
  }, [novel?.id, messageApi]);

  if (loading) {
    return <LoadingState />;
  }

  if (error || !novel || !id) {
    return (
      <ErrorState
        error={error}
        title="Failed to load novel details"
        onRetry={() => {
          setLoading(true);
          setRefreshId((v) => v + 1);
        }}
      />
    );
  }

  return (
    <Space direction="vertical" size={lg ? 'large' : 'small'}>
      {contextHolder}
      <NovelDetailsCard novel={novel} showActions />
      <VolumeListCard novelId={novel.id} />
      <ArtifactListCard artifacts={artifacts} />
    </Space>
  );
};
