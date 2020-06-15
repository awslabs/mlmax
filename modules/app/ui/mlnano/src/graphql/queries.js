/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const getDataSet = /* GraphQL */ `
  query GetDataSet($id: ID!) {
    getDataSet(id: $id) {
      id
      name
      description
      fileKey
      createdAt
      updatedAt
      owner
    }
  }
`;
export const listDataSets = /* GraphQL */ `
  query ListDataSets(
    $filter: ModelDataSetFilterInput
    $limit: Int
    $nextToken: String
  ) {
    listDataSets(filter: $filter, limit: $limit, nextToken: $nextToken) {
      items {
        id
        name
        description
        fileKey
        createdAt
        updatedAt
        owner
      }
      nextToken
    }
  }
`;
